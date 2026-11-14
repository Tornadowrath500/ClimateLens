"""Plain, explicit classification, cost and group-outcome metrics.

Conventions: label 1 = Good risk (the favorable prediction), label 2 = Bad risk.
Every rate has an explicit denominator; none is a verdict on fairness.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from fairlens.config import (
    BAD_RISK_LABEL,
    COST_BAD_PREDICTED_GOOD,
    COST_GOOD_PREDICTED_BAD,
    GOOD_RISK_LABEL,
)

DEFAULT_GRID = np.round(np.arange(0.05, 0.951, 0.01), 2)


def _as_1d(y_true, y_pred) -> tuple[np.ndarray, np.ndarray]:
    actual, predicted = np.asarray(y_true), np.asarray(y_pred)
    if actual.ndim != 1 or predicted.ndim != 1 or actual.shape != predicted.shape:
        raise ValueError("y_true and y_pred must be one-dimensional arrays of equal shape.")
    return actual, predicted


def predict_from_proba(p_good, threshold: float) -> np.ndarray:
    """Predict Good (1) when P(Good) >= threshold, otherwise Bad (2)."""
    return np.where(np.asarray(p_good, dtype=float) >= threshold, GOOD_RISK_LABEL, BAD_RISK_LABEL)


def confusion_counts(y_true, y_pred) -> dict[str, int]:
    """Named confusion cells (rows = actual label, columns = predicted label)."""
    actual, predicted = _as_1d(y_true, y_pred)
    good, pred_good = actual == GOOD_RISK_LABEL, predicted == GOOD_RISK_LABEL
    return {
        "good_as_good": int((good & pred_good).sum()),
        "good_as_bad": int((good & ~pred_good).sum()),
        "bad_as_good": int((~good & pred_good).sum()),
        "bad_as_bad": int((~good & ~pred_good).sum()),
    }


def uci_cost(y_true, y_pred) -> float:
    """Total UCI cost: 5 per actually-Bad case predicted Good, 1 per Good predicted Bad."""
    c = confusion_counts(y_true, y_pred)
    return float(COST_BAD_PREDICTED_GOOD * c["bad_as_good"] + COST_GOOD_PREDICTED_BAD * c["good_as_bad"])


def cost_per_applicant(y_true, y_pred) -> float:
    n = len(np.asarray(y_true))
    return uci_cost(y_true, y_pred) / n if n else float("nan")


def theoretical_cost_threshold() -> float:
    """Threshold minimizing expected cost IF probabilities were perfectly calibrated.

    Predicting Good costs 5*(1-p); predicting Bad costs 1*p; Good is cheaper when p > 5/6.
    """
    return COST_BAD_PREDICTED_GOOD / (COST_BAD_PREDICTED_GOOD + COST_GOOD_PREDICTED_BAD)


def classification_summary(y_true, y_pred, *, positive_label: int = GOOD_RISK_LABEL, p_good=None) -> dict:
    """Common metrics; the positive class is always named. AUC needs p_good."""
    actual, predicted = _as_1d(y_true, y_pred)
    other = BAD_RISK_LABEL if positive_label == GOOD_RISK_LABEL else GOOD_RISK_LABEL
    counts = confusion_counts(actual, predicted)
    summary = {
        "n": int(len(actual)),
        "accuracy": float(accuracy_score(actual, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
        "precision": float(precision_score(actual, predicted, pos_label=positive_label, zero_division=0)),
        "recall": float(recall_score(actual, predicted, pos_label=positive_label, zero_division=0)),
        "f1": float(f1_score(actual, predicted, pos_label=positive_label, zero_division=0)),
        "precision_other": float(precision_score(actual, predicted, pos_label=other, zero_division=0)),
        "recall_other": float(recall_score(actual, predicted, pos_label=other, zero_division=0)),
        "confusion": counts,
        # Fixed label order [Good, Bad] so the matrix is always 2x2.
        "confusion_matrix": [
            [counts["good_as_good"], counts["good_as_bad"]],
            [counts["bad_as_good"], counts["bad_as_bad"]],
        ],
        "cost_total": uci_cost(actual, predicted),
        "cost_per_applicant": cost_per_applicant(actual, predicted),
        "predicted_good_rate": float((predicted == GOOD_RISK_LABEL).mean()),
    }
    if p_good is not None and len(np.unique(actual)) == 2:
        summary["auc"] = float(roc_auc_score(actual == GOOD_RISK_LABEL, p_good))
    else:
        summary["auc"] = float("nan")
    return summary


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a proportion; (nan, nan) when n == 0."""
    if n <= 0:
        return (float("nan"), float("nan"))
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))


def _rate(num: int, den: int) -> float:
    return float(num / den) if den else float("nan")


def group_outcome_metrics(y_true, y_pred, groups, *, good_label: int = GOOD_RISK_LABEL) -> pd.DataFrame:
    """Compare model outcomes by group, with denominators and 95% Wilson intervals.

    predicted_good_rate is the share *classified* Good: a proxy for the favorable
    prediction, not an actual loan approval rate. Descriptive only: it does not
    prove discrimination, causation, legal noncompliance or real-world impact.
    """
    actual, predicted = np.asarray(y_true), np.asarray(y_pred)
    group_values = (
        pd.Series(groups, dtype="object").reset_index(drop=True).fillna("Missing / unknown").astype(str)
    )
    if actual.ndim != 1 or predicted.ndim != 1 or len(actual) != len(predicted):
        raise ValueError("y_true and y_pred must be one-dimensional arrays of equal length.")
    if len(group_values) != len(actual):
        raise ValueError("groups must have the same number of values as y_true.")
    if len(actual) == 0:
        raise ValueError("Cannot audit an empty sample.")

    frame = pd.DataFrame({"actual": actual, "predicted": predicted, "group": group_values})
    rows = []
    for name, part in frame.groupby("group", sort=True, dropna=False):
        a_good = part["actual"].to_numpy() == good_label
        p_good = part["predicted"].to_numpy() == good_label
        n, n_good, n_bad = len(part), int(a_good.sum()), int((~a_good).sum())
        pred_good = int(p_good.sum())
        false_good = int((p_good & ~a_good).sum())
        false_bad = int((~p_good & a_good).sum())
        row = {
            "group": str(name),
            "sample_count": int(n),
            "actual_good_count": n_good,
            "actual_bad_count": n_bad,
            "actual_good_rate": _rate(n_good, n),
            "predicted_good_count": pred_good,
            "predicted_good_rate": _rate(pred_good, n),
            "false_good_count": false_good,
            "false_good_rate_among_bad": _rate(false_good, n_bad),
            "false_bad_count": false_bad,
            "false_bad_rate_among_good": _rate(false_bad, n_good),
            "cost_per_applicant": (
                COST_BAD_PREDICTED_GOOD * false_good + COST_GOOD_PREDICTED_BAD * false_bad
            ) / n,
        }
        for key, k, d in (
            ("predicted_good", pred_good, n),
            ("false_good", false_good, n_bad),
            ("false_bad", false_bad, n_good),
        ):
            row[f"{key}_ci_low"], row[f"{key}_ci_high"] = wilson_interval(k, d)
        rows.append(row)
    return pd.DataFrame(rows)


def intervals_overlap(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """True when two intervals overlap (or either is undefined)."""
    if any(math.isnan(x) for x in (*a, *b)):
        return True
    return a[0] <= b[1] and b[0] <= a[1]


def age_gap(metrics: pd.DataFrame, younger: str, older: str) -> dict[str, float]:
    """Younger-minus-older differences for the three group measures (nan if a group is absent)."""
    table = metrics.set_index("group")
    out = {}
    for key in ("predicted_good_rate", "false_good_rate_among_bad", "false_bad_rate_among_good"):
        try:
            out[key] = float(table.loc[younger, key] - table.loc[older, key])
        except KeyError:
            out[key] = float("nan")
    return out


def _rates(actual_good: np.ndarray, pred_good: np.ndarray) -> dict:
    n = len(actual_good)
    bad = ~actual_good
    fg, fb = int((pred_good & bad).sum()), int((~pred_good & actual_good).sum())
    return {
        "n": n,
        "predicted_good_rate": float(pred_good.mean()) if n else float("nan"),
        "false_good_rate_among_bad": _rate(fg, int(bad.sum())),
        "false_bad_rate_among_good": _rate(fb, int(actual_good.sum())),
        "accuracy": float((pred_good == actual_good).mean()) if n else float("nan"),
        "cost_per_applicant": (COST_BAD_PREDICTED_GOOD * fg + COST_GOOD_PREDICTED_BAD * fb) / n if n else float("nan"),
    }


def threshold_sweep(y_true, p_good, groups, thresholds=DEFAULT_GRID) -> pd.DataFrame:
    """Long table of outcomes at each single threshold, overall ('All') and per group."""
    actual_good = np.asarray(y_true) == GOOD_RISK_LABEL
    p = np.asarray(p_good, dtype=float)
    g = pd.Series(groups, dtype="object").astype(str).to_numpy()
    if not (len(actual_good) == len(p) == len(g)):
        raise ValueError("y_true, p_good and groups must have equal length.")
    masks = {"All": np.ones(len(p), dtype=bool)} | {name: g == name for name in sorted(set(g))}
    rows = []
    for t in thresholds:
        pred_good = p >= t
        for name, mask in masks.items():
            rows.append({"threshold": float(t), "group": name, **_rates(actual_good[mask], pred_good[mask])})
    return pd.DataFrame(rows)


def best_threshold_by_cost(y_true, p_good, grid=DEFAULT_GRID) -> tuple[float, float]:
    """(threshold, cost_per_applicant) minimizing cost on the data given.

    Call with VALIDATION data only. Ties resolve toward 0.5.
    """
    actual_good = np.asarray(y_true) == GOOD_RISK_LABEL
    p = np.asarray(p_good, dtype=float)
    costs = np.array([_rates(actual_good, p >= t)["cost_per_applicant"] for t in grid])
    best = np.flatnonzero(costs <= costs.min() + 1e-12)
    pick = best[np.argmin(np.abs(np.asarray(grid)[best] - 0.5))]
    return float(grid[pick]), float(costs[pick])
