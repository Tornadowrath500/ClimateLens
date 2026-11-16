"""Audit your own model: validated, in-memory CSV uploads (never written to disk) and the group comparison."""

from __future__ import annotations

import io
import os
import re
import secrets

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from backend import state
from backend.errors import ServiceError
from backend.services.common import context, respond, source_info
from fairlens.byom import FOUR_FIFTHS, SMALL_GROUP, group_table, plain_summary, to_favorable

MAX_UPLOAD_BYTES = int(float(os.environ.get("FAIRLENS_MAX_UPLOAD_MB", "5")) * 1024 * 1024)
MAX_ROWS, MAX_COLUMNS, MAX_LEVELS_SHOWN = 200_000, 200, 50


def _clean_name(name: str | None) -> str:
    base = re.split(r"[\\/]", name or "upload.csv")[-1]
    return re.sub(r"[^\w .()\-]", "_", base)[:120] or "upload.csv"


def _column_info(df: pd.DataFrame) -> list[dict]:
    out = []
    for c in df.columns:
        s, numeric = df[c], is_numeric_dtype(df[c])
        levels = sorted(s.dropna().astype(str).unique())
        info = {"name": str(c), "numeric": bool(numeric), "n_unique": int(s.nunique(dropna=True)),
                "values": levels[:MAX_LEVELS_SHOWN], "values_truncated": len(levels) > MAX_LEVELS_SHOWN,
                "min": None, "max": None, "median": None}
        if numeric and s.notna().any():
            info.update(min=float(s.min()), max=float(s.max()), median=float(s.median()))
        out.append(info)
    return out


def _register(session_id, df: pd.DataFrame, name: str, extra: dict | None = None) -> dict:
    upload_id = secrets.token_urlsafe(12)
    state.add_upload(session_id, upload_id, {"df": df, "name": name})
    return respond(source_info("real"), {"upload_id": upload_id, "name": name, "rows": int(len(df)),
                                          "n_columns": int(df.shape[1]), "columns": _column_info(df), **(extra or {})})


def byom_upload(session_id: str | None, filename: str | None, content: bytes) -> dict:
    state.get_session(session_id)
    name = _clean_name(filename)
    if not name.lower().endswith(".csv"):
        raise ServiceError(422, "invalid_file_type", "Upload a .csv file.")
    if not content:
        raise ServiceError(422, "invalid_csv", "The file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ServiceError(413, "file_too_large", f"The file is larger than {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
                           {"max_bytes": MAX_UPLOAD_BYTES})
    try:
        df = pd.read_csv(io.StringIO(content.decode("utf-8", errors="replace")), nrows=MAX_ROWS + 1)
    except Exception as exc:
        raise ServiceError(422, "invalid_csv", "The file could not be read as a CSV.") from exc
    if len(df) < 2:
        raise ServiceError(422, "invalid_csv", "The file needs at least two rows.")
    if len(df) > MAX_ROWS or df.shape[1] > MAX_COLUMNS:
        raise ServiceError(413, "file_too_large", f"The file may have at most {MAX_ROWS:,} rows and {MAX_COLUMNS} columns.")
    return _register(session_id, df, name)


def byom_sample(session_id: str | None, source: str = "real", model: str = "Logistic regression", excluded=()) -> dict:
    """FairLens's own validation predictions as a ready-made sample file, with the selections the page pre-filled."""
    ctx = context(source, model, excluded)
    p = ctx.audit.proba(model, "validation")
    df = pd.DataFrame({"approved": (p >= 0.5).astype(int), "score": p.round(4),
                       "actually_good": (ctx.audit.y("validation") == 1).astype(int),
                       "age_group": ctx.audit.groups("validation")})
    out = _register(session_id, df, "FairLens validation sample")
    out["data_source"] = ctx.info
    out["suggested"] = {"decision_column": "approved", "group_column": "age_group", "truth_column": "actually_good",
                        "favorable_value": "1", "truth_positive_value": "1"}
    return out


def byom_audit(session_id: str | None, upload_id: str, decision_column: str, group_column: str,
               truth_column: str | None = None, favorable_value: str | None = None, threshold: float | None = None,
               truth_positive_value: str | None = None, reference_group: str | None = None) -> dict:
    df = state.get_upload(session_id, upload_id)["df"]
    for label, col in (("decision_column", decision_column), ("group_column", group_column)):
        if col not in df.columns:
            raise ServiceError(422, "unknown_column", f"{label} {col!r} is not a column of the uploaded file.")
    if decision_column == group_column:
        raise ServiceError(422, "invalid_columns", "The decision and group columns must be different.")
    if truth_column is not None and (truth_column not in df.columns or truth_column in (decision_column, group_column)):
        raise ServiceError(422, "unknown_column", "truth_column must be a different column of the uploaded file.")

    levels = sorted(df[group_column].dropna().astype(str).unique())
    if not 2 <= len(levels) <= 20:
        raise ServiceError(422, "invalid_group_column",
                           f"The group column has {len(levels)} distinct values; choose a column with between 2 and 20.")
    numeric_score = is_numeric_dtype(df[decision_column]) and df[decision_column].nunique() > 2
    try:
        if numeric_score:
            thr = float(df[decision_column].median()) if threshold is None else float(threshold)
            fav, mode = to_favorable(df[decision_column], None, thr), "score"
        else:
            values = sorted(df[decision_column].dropna().astype(str).unique())
            fv = values[-1] if favorable_value is None else str(favorable_value)
            if fv not in values:
                raise ServiceError(422, "invalid_favorable_value", "favorable_value is not a value in the decision column.",
                                   {"allowed": values[:MAX_LEVELS_SHOWN]})
            fav, mode, thr = to_favorable(df[decision_column], fv), "label", None
    except (ValueError, TypeError) as exc:
        raise ServiceError(422, "invalid_decision_column", "The decision column could not be interpreted as scores or labels.") from exc

    actual = None
    if truth_column is not None:
        tv = sorted(df[truth_column].dropna().astype(str).unique())
        tpos = tv[-1] if truth_positive_value is None else str(truth_positive_value)
        if tpos not in tv:
            raise ServiceError(422, "invalid_truth_value", "truth_positive_value is not a value in the truth column.",
                               {"allowed": tv[:MAX_LEVELS_SHOWN]})
        actual = (df[truth_column].astype(str) == tpos).to_numpy()

    if reference_group is not None and reference_group not in levels:
        raise ServiceError(422, "invalid_reference_group", "reference_group is not a value in the group column.", {"allowed": levels})
    table = group_table(fav, df[group_column], actual, reference_group)
    return respond(source_info("real"), {
        "mode": mode, "threshold_used": thr, "n_rows": int(len(df)), "has_truth": actual is not None,
        "reference": table["reference"].iloc[0], "small_group_limit": SMALL_GROUP, "four_fifths": FOUR_FIFTHS,
        "findings": plain_summary(table), "table": table,
    })
