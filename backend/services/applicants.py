"""Applicant map and applicant simulator."""

from __future__ import annotations

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from backend import state
from backend.errors import ServiceError
from backend.services.common import context, respond, source_info
from fairlens.applicant import best_single_changes, explain, greedy_path, score, sensitive_flip_test
from fairlens.config import AGE_COLUMN, FEATURE_DICTIONARY, TARGET_COLUMN, feature_label, value_label
from fairlens.data import group_labels, make_age_groups
from fairlens.evaluation import OperatingPoint
from fairlens.mapview import KIND_FALSE_BAD, KIND_FALSE_GOOD, KIND_OK, build_map, look_alikes, terrain, terrain_summary


# ---- applicant map -----------------------------------------------------------------------------------
def _get_map(ctx, include_train: bool):
    per_group = tuple(sorted((ctx.op.per_group or {}).items()))
    key = ("map", ctx.audit_key, ctx.model, ctx.op.threshold, per_group, include_train)
    return state.derived(key, lambda: build_map(ctx.audit, ctx.model, ctx.op, include_train))


def _int_in(value, name: str, lo: int, hi: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise ServiceError(422, "invalid_parameter", f"{name} must be an integer from {lo} to {hi}.")
    return value


def map_build(source="real", model="Logistic regression", excluded=(), decision_rule=None,
              include_train: bool = False, bins: int = 5, min_per_group: int = 5) -> dict:
    bins, min_per_group = _int_in(bins, "bins", 2, 12), _int_in(min_per_group, "min_per_group", 1, 100)
    ctx = context(source, model, excluded, decision_rule)
    md = _get_map(ctx, bool(include_train))
    t = terrain(md.frame, bins, min_per_group)
    points = md.frame.assign(i=np.arange(len(md.frame)))
    return respond(ctx, {
        "n": int(len(points)), "include_train": bool(include_train), "bins": bins, "min_per_group": min_per_group,
        "explained": list(md.explained), "groups": dict(zip(("young", "old"), group_labels())),
        "kinds": {"ok": KIND_OK, "false_good": KIND_FALSE_GOOD, "false_bad": KIND_FALSE_BAD},
        "points": points[["i", "x", "y", "p_good", "pred_good", "actual_good", "group", "kind", "part"]],
        "terrain": t, "terrain_summary": terrain_summary(t),
    })


def map_applicant(source="real", model="Logistic regression", excluded=(), decision_rule=None,
                  include_train: bool = False, index: int = 0) -> dict:
    ctx = context(source, model, excluded, decision_rule)
    md = _get_map(ctx, bool(include_train))
    n = len(md.frame)
    index = _int_in(index, "index", 0, n - 1)
    row, frame = md.X.iloc[[index]], md.frame
    pipe, train = ctx.audit.pipelines[model], ctx.audit.splits.X_train
    group = frame.loc[index, "group"]
    thr = ctx.op.per_group.get(group, ctx.op.threshold) if ctx.op.per_group else ctx.op.threshold
    steps, p_end, flipped = greedy_path(pipe, row, train, thr)
    raw = row.iloc[0].to_dict()
    return respond(ctx, {
        "index": index, "group": group, "actual_good": bool(frame.loc[index, "actual_good"]), "part": frame.loc[index, "part"],
        "score": score(pipe, row), "threshold": thr,
        "profile": [{"column": c, "label": feature_label(c), "value": value_label(c, raw[c]), "raw": raw[c]} for c in row.columns],
        "raw": raw, "explain": explain(pipe, row, train), "look_alikes": look_alikes(md, index),
        "path": {"steps": steps, "p_end": p_end, "flipped": flipped},
    })


# ---- applicant simulator -----------------------------------------------------------------------------
def _features(source: str):
    data, _ = state.get_dataset(source)
    return data.drop(columns=[TARGET_COLUMN])


def _spec(X: pd.DataFrame) -> list[dict]:
    out = []
    for c in X.columns:
        label, _, desc = FEATURE_DICTIONARY[c]
        if is_numeric_dtype(X[c]):
            out.append({"column": c, "label": label, "description": desc, "type": "numeric",
                        "min": int(X[c].min()), "max": int(X[c].max()), "levels": []})
        else:
            out.append({"column": c, "label": label, "description": desc, "type": "categorical", "min": None, "max": None,
                        "levels": [{"value": v, "label": value_label(c, v)} for v in sorted(X[c].unique())]})
    return out


def _as_profile(spec: list[dict], base: dict) -> dict:
    """Clamp a raw row into what the form can show (the Streamlit slider/selectbox defaults)."""
    out = {}
    for f in spec:
        v = base[f["column"]]
        if f["type"] == "numeric":
            out[f["column"]] = int(min(max(float(v), f["min"]), f["max"]))
        else:
            levels = [lv["value"] for lv in f["levels"]]
            out[f["column"]] = v if v in levels else levels[0]
    return out


def _typical(train: pd.DataFrame) -> dict:
    return {c: (float(train[c].median()) if is_numeric_dtype(train[c]) else train[c].mode().iloc[0]) for c in train.columns}


def simulator_schema(source: str = "real") -> dict:
    audit, _ = state.get_audit(source, ())
    X = _features(source)
    spec = _spec(X)
    return respond(source_info(source), {
        "features": spec, "typical": _as_profile(spec, _typical(audit.splits.X_train)), "start_label": "a typical applicant",
    })


def simulator_random(source: str = "real") -> dict:
    audit, _ = state.get_audit(source, ())
    spec = _spec(_features(source))
    row = audit.splits.X_train.sample(1).iloc[0].to_dict()
    return respond(source_info(source), {"profile": _as_profile(spec, row), "start_label": "a randomly drawn applicant"})


def _profile_to_row(profile: dict, X: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(profile, dict):
        raise ServiceError(422, "invalid_profile", "profile must be an object mapping each input to a value.")
    missing, unknown = [c for c in X.columns if c not in profile], [c for c in profile if c not in X.columns]
    if missing or unknown:
        raise ServiceError(422, "invalid_profile", "profile must contain exactly the model's 20 inputs.",
                           {"missing": missing, "unknown": unknown})
    values = {}
    for c in X.columns:
        v = profile[c]
        if is_numeric_dtype(X[c]):
            lo, hi = int(X[c].min()), int(X[c].max())
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v) or not lo <= v <= hi:
                raise ServiceError(422, "invalid_profile", f"{feature_label(c)} must be a number from {lo} to {hi}.", {"column": c})
        elif v not in set(X[c].unique()):
            raise ServiceError(422, "invalid_profile", f"{feature_label(c)} has an unknown value.", {"column": c})
        values[c] = v
    return pd.DataFrame([values])[X.columns].astype(X.dtypes.to_dict())


def simulator_evaluate(source="real", model="Logistic regression", excluded=(), decision_rule=None, profile=None) -> dict:
    ctx = context(source, model, excluded, decision_rule)
    X = ctx.data.drop(columns=[TARGET_COLUMN])
    row = _profile_to_row(profile, X)
    pipe, train = ctx.audit.pipelines[model], ctx.audit.splits.X_train
    group = make_age_groups(row[AGE_COLUMN]).iloc[0]
    thr = ctx.op.per_group.get(group, ctx.op.threshold) if ctx.op.per_group else ctx.op.threshold
    p = score(pipe, row)
    steps, p_end, flipped = greedy_path(pipe, row, train, thr)
    twin = sensitive_flip_test(pipe, row, train, thr)
    return respond(ctx, {
        "score": p, "threshold": thr, "decision": "Good" if p >= thr else "Bad", "group": group,
        "explain": explain(pipe, row, train), "changes": best_single_changes(pipe, row, train, thr),
        "path": {"steps": steps, "p_end": p_end, "flipped": flipped},
        "twin": twin, "twin_flips": int(twin["decision_changes"].sum()),
    })