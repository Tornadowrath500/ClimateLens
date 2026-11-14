"""Strategy comparison: reweighing, input removal and threshold what-ifs, all scored on VALIDATION data.

These are experiments that show trade-offs. None of them is a guaranteed fairness fix.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from fairlens.config import AGE_COLUMN, GOOD_RISK_LABEL, PERSONAL_STATUS_COLUMN, RANDOM_STATE, TARGET_COLUMN
from fairlens.data import group_labels, make_age_groups
from fairlens.evaluation import OperatingPoint, run_audit
from fairlens.metrics import DEFAULT_GRID, best_threshold_by_cost, classification_summary, group_outcome_metrics
from fairlens.models import build_model, prob_good


@dataclass
class Strategy:
    name: str
    blurb: str
    p: np.ndarray
    op: OperatingPoint
    caution: str = ""


def reweighing_weights(y, groups) -> np.ndarray:
    """Kamiran-Calders reweighing: weight = P(group) P(label) / P(group, label), so group and label look independent."""
    df = pd.DataFrame({"y": np.asarray(y), "g": np.asarray(groups)})
    pg, py = df["g"].value_counts(normalize=True), df["y"].value_counts(normalize=True)
    pgy = df.value_counts(normalize=True)
    return np.array([pg[g] * py[y_] / pgy.loc[(y_, g)] for y_, g in zip(df["y"], df["g"])])


def equal_opportunity_thresholds(y, p, groups, base: float = 0.5) -> dict[str, float]:
    """Keep the older group at `base`; pick the younger threshold whose Good-recall best matches (validation)."""
    young, old = group_labels()
    y, p, g = np.asarray(y), np.asarray(p), np.asarray(groups)
    def recall(mask, t):
        m = mask & (y == GOOD_RISK_LABEL)
        return float((p[m] >= t).mean()) if m.any() else np.nan
    target = recall(g == old, base)
    errs = [(abs(recall(g == young, t) - target), abs(t - base), t) for t in DEFAULT_GRID]
    return {young: float(min(errs)[2]), old: base}


def build_strategies(data: pd.DataFrame, model_name: str, seed: int = RANDOM_STATE) -> tuple[dict[str, Strategy], np.ndarray, np.ndarray]:
    """Fit every strategy on the SAME training split; return strategies plus validation labels and groups."""
    base = run_audit(data, (), seed, (model_name,))
    s = base.splits
    y, g = s.y_validation.to_numpy(), base.groups("validation")
    p0 = base.proba(model_name, "validation")
    t_best, _ = best_threshold_by_cost(y, p0)
    noinputs = run_audit(data, (AGE_COLUMN, PERSONAL_STATUS_COLUMN), seed, (model_name,))
    w = reweighing_weights(s.y_train, make_age_groups(s.X_train[AGE_COLUMN]))
    rw = build_model(model_name, s.X_train).fit(s.X_train, s.y_train, model__sample_weight=w)
    p_rw = prob_good(rw, s.X_validation)
    p_noin = noinputs.proba(model_name, "validation")
    t_eo = equal_opportunity_thresholds(y, p0, g)
    out = [
        Strategy("Baseline", "Standard model, one threshold of 0.50.", p0, OperatingPoint(0.5)),
        Strategy("Cost-tuned threshold", "Same model; threshold chosen on validation data to minimise the UCI cost.", p0, OperatingPoint(t_best)),
        Strategy("Remove age and status", "Retrain without the two sensitive inputs. Proxies may still carry the same information.", p_noin, OperatingPoint(0.5)),
        Strategy("Reweighing", "Retrain with training weights that make group and label look statistically independent.", p_rw, OperatingPoint(0.5)),
        Strategy("Reweighing + cost threshold", "Reweighed model with a validation cost-tuned threshold.", p_rw, OperatingPoint(best_threshold_by_cost(y, p_rw)[0])),
        Strategy("Group thresholds (what-if)", "Separate thresholds chosen so Good-recall matches between groups.", p0, OperatingPoint(0.5, t_eo),
                 "Using age to set different cut-offs can itself raise legal and ethical concerns. Shown only to expose the trade-off."),
    ]
    return {x.name: x for x in out}, y, g


def _rates(actual_good: np.ndarray, pred_good: np.ndarray) -> tuple[float, float, float]:
    bad, good = ~actual_good, actual_good
    pg = pred_good.mean() if len(pred_good) else np.nan
    fg = (pred_good & bad).sum() / bad.sum() if bad.any() else np.nan
    fb = (~pred_good & good).sum() / good.sum() if good.any() else np.nan
    return float(pg), float(fg), float(fb)


def bootstrap_gap_ci(y, pred, groups, metric: int = 0, n: int = 400, seed: int = 0) -> tuple[float, float]:
    """95% bootstrap interval for (younger - older) in metric 0=classified-Good, 1=false-Good, 2=false-Bad rate."""
    young, old = group_labels()
    rng = np.random.default_rng(seed)
    ag, pg, g = np.asarray(y) == GOOD_RISK_LABEL, np.asarray(pred) == GOOD_RISK_LABEL, np.asarray(groups)
    iy, io = np.flatnonzero(g == young), np.flatnonzero(g == old)
    vals = []
    for _ in range(n):
        a, b = rng.choice(iy, len(iy)), rng.choice(io, len(io))
        vals.append(_rates(ag[a], pg[a])[metric] - _rates(ag[b], pg[b])[metric])
    return tuple(np.nanpercentile(vals, [2.5, 97.5]))


def evaluate_strategies(strategies: dict[str, Strategy], y, g) -> pd.DataFrame:
    young, old = group_labels()
    rows = []
    for st_ in strategies.values():
        pred = st_.op.apply(st_.p, g)
        s = classification_summary(y, pred, p_good=st_.p)
        m = group_outcome_metrics(y, pred, g).set_index("group")
        row = {"strategy": st_.name, "cost_per_applicant": s["cost_per_applicant"], "accuracy": s["accuracy"], "auc": s.get("auc", np.nan)}
        for key, label in (("predicted_good_rate", "gap_classified_good"), ("false_good_rate_among_bad", "gap_false_good"), ("false_bad_rate_among_good", "gap_false_bad")):
            row[label] = float(m.loc[young, key] - m.loc[old, key]) if {young, old} <= set(m.index) else np.nan
        lo, hi = bootstrap_gap_ci(y, pred, g, 0, n=300)
        row["gap_classified_good_lo"], row["gap_classified_good_hi"] = lo, hi
        rows.append(row)
    return pd.DataFrame(rows)
