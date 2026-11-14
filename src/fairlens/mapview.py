"""The Applicant Map: applicants placed by similarity, plus a 'fairness terrain' of look-alike regions.

Position is a 2-D PCA of the NON-sensitive inputs (age and personal status are left out), so two
applicants close together look alike on everything except those inputs. If look-alikes from different age
groups are classified differently, that is a *signal to investigate* (it does not prove discrimination).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from fairlens.config import AGE_COLUMN, GOOD_RISK_LABEL, PERSONAL_STATUS_COLUMN, RANDOM_STATE
from fairlens.data import group_labels, make_age_groups
from fairlens.models import build_preprocessor, prob_good

KIND_OK, KIND_FALSE_GOOD, KIND_FALSE_BAD = "Correct", "Bad case classified Good (costly)", "Good case classified Bad"


@dataclass
class MapData:
    frame: pd.DataFrame      # one row per applicant: x, y, p_good, pred_good, actual_good, group, kind, part, row_id
    Z: np.ndarray            # standardised non-sensitive features (for look-alike search)
    X: pd.DataFrame          # raw inputs aligned with frame rows
    explained: tuple[float, float]


def _dense(a):
    return a.toarray() if hasattr(a, "toarray") else np.asarray(a)


def build_map(audit, model_name: str, op, include_train: bool = False) -> MapData:
    s = audit.splits
    pre = build_preprocessor(s.X_train, exclude=(AGE_COLUMN, PERSONAL_STATUS_COLUMN)).fit(s.X_train)
    pca = PCA(n_components=2, random_state=RANDOM_STATE).fit(_dense(pre.transform(s.X_train)))
    pipe = audit.pipelines[model_name]
    parts = [("validation", s.X_validation, s.y_validation)]
    if include_train:
        parts.append(("training", s.X_train, s.y_train))
    X = pd.concat([p[1] for p in parts])
    y = pd.concat([p[2] for p in parts]).to_numpy()
    Z = _dense(pre.transform(X))
    xy = pca.transform(Z)
    p = prob_good(pipe, X)
    g = make_age_groups(X[AGE_COLUMN]).to_numpy()
    pred_good = op.apply(p, g) == GOOD_RISK_LABEL
    actual_good = y == GOOD_RISK_LABEL
    kind = np.where(pred_good == actual_good, KIND_OK, np.where(pred_good & ~actual_good, KIND_FALSE_GOOD, KIND_FALSE_BAD))
    frame = pd.DataFrame({
        "row_id": X.index.to_numpy(), "part": np.concatenate([[n] * len(px) for n, px, _ in parts]),
        "x": xy[:, 0], "y": xy[:, 1], "p_good": p, "pred_good": pred_good, "actual_good": actual_good, "group": g, "kind": kind,
    }).reset_index(drop=True)
    return MapData(frame, Z, X.reset_index(drop=True), tuple(float(v) for v in pca.explained_variance_ratio_))


def terrain(frame: pd.DataFrame, bins: int = 5, min_per_group: int = 5) -> pd.DataFrame:
    """Grid of look-alike regions. gap = younger classified-Good rate minus older rate, but only where
    BOTH groups have at least `min_per_group` applicants; elsewhere the gap is left blank on purpose."""
    young, old = group_labels()
    xe = np.linspace(frame["x"].min() - 1e-9, frame["x"].max() + 1e-9, bins + 1)
    ye = np.linspace(frame["y"].min() - 1e-9, frame["y"].max() + 1e-9, bins + 1)
    f = frame.assign(cx=np.clip(np.digitize(frame["x"], xe) - 1, 0, bins - 1), cy=np.clip(np.digitize(frame["y"], ye) - 1, 0, bins - 1))
    rows = []
    for (cx, cy), part in f.groupby(["cx", "cy"]):
        a, b = part[part["group"] == young], part[part["group"] == old]
        row = {"cx": int(cx), "cy": int(cy), "x": float((xe[cx] + xe[cx + 1]) / 2), "y": float((ye[cy] + ye[cy + 1]) / 2),
               "n_young": len(a), "n_old": len(b), "rate_young": a["pred_good"].mean() if len(a) else np.nan,
               "rate_old": b["pred_good"].mean() if len(b) else np.nan}
        row["reliable"] = len(a) >= min_per_group and len(b) >= min_per_group
        row["gap"] = row["rate_young"] - row["rate_old"] if row["reliable"] else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def terrain_summary(t: pd.DataFrame) -> dict:
    ok = t[t["reliable"]]
    if ok.empty:
        return {"regions": 0}
    w = ok["n_young"] + ok["n_old"]
    return {"regions": int(len(ok)), "weighted_gap": float(np.average(ok["gap"], weights=w)),
            "worst": ok.loc[ok["gap"].idxmin()].to_dict(), "regions_total": int(len(t)),
            "applicants_covered": int(w.sum())}


def look_alikes(md: MapData, i: int, k: int = 15) -> dict:
    """k nearest look-alikes to applicant i, from the same and from the other age group."""
    g = md.frame["group"].to_numpy()
    d = np.linalg.norm(md.Z - md.Z[i], axis=1)
    d[i] = np.inf
    out = {}
    for label, mask in (("same", g == g[i]), ("other", g != g[i])):
        idx = np.flatnonzero(mask)
        idx = idx[np.argsort(d[idx])][:k]
        sub = md.frame.iloc[idx]
        out[label] = {"n": len(idx), "classified_good": float(sub["pred_good"].mean()) if len(idx) else np.nan,
                      "actual_good": float(sub["actual_good"].mean()) if len(idx) else np.nan,
                      "mean_p_good": float(sub["p_good"].mean()) if len(idx) else np.nan, "ids": idx.tolist()}
    return out
