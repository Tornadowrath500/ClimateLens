"""Plain, explicit classification and group-outcome metrics."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def classification_summary(y_true, y_pred, *, positive_label: int) -> dict:
    """Return common classification metrics; callers must name the positive class."""
    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)
    if actual.ndim != 1 or predicted.ndim != 1 or actual.shape != predicted.shape:
        raise ValueError("y_true and y_pred must be one-dimensional arrays of equal shape.")
    labels = np.unique(np.concatenate([actual, predicted]))
    return {
        "accuracy": float(accuracy_score(actual, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(actual, predicted)),
        "precision": float(precision_score(actual, predicted, pos_label=positive_label, zero_division=0)),
        "recall": float(recall_score(actual, predicted, pos_label=positive_label, zero_division=0)),
        "f1": float(f1_score(actual, predicted, pos_label=positive_label, zero_division=0)),
        "confusion_matrix": confusion_matrix(actual, predicted, labels=labels).tolist(),
    }


def group_outcome_metrics(y_true, y_pred, groups, *, good_label: int = 1) -> pd.DataFrame:
    """Compare model outcomes by group; the predicted-Good rate is an approval proxy.

    These are descriptive historical-benchmark metrics. They do not prove
    discrimination, causation, legal noncompliance, or real-world lending impact.
    """
    actual = np.asarray(y_true)
    predicted = np.asarray(y_pred)
    group_values = (
        pd.Series(groups, dtype="object")
        .reset_index(drop=True)
        .fillna("Missing / unknown")
        .astype(str)
    )

    if actual.ndim != 1 or predicted.ndim != 1 or len(actual) != len(predicted):
        raise ValueError("y_true and y_pred must be one-dimensional arrays of equal length.")
    if len(group_values) != len(actual):
        raise ValueError("groups must have the same number of values as y_true.")
    if len(actual) == 0:
        raise ValueError("Cannot audit an empty sample.")

    frame = pd.DataFrame({"actual": actual, "predicted": predicted, "group": group_values})
    rows = []

    for group_name, part in frame.groupby("group", sort=True, dropna=False):
        actual_good = part["actual"].to_numpy() == good_label
        predicted_good = part["predicted"].to_numpy() == good_label
        actual_bad = ~actual_good
        actual_good_count = int(actual_good.sum())
        actual_bad_count = int(actual_bad.sum())
        rows.append(
            {
                "group": str(group_name),
                "sample_count": int(len(part)),
                "actual_good_rate": float(actual_good.mean()),
                "predicted_good_rate": float(predicted_good.mean()),
                "false_good_rate_among_bad": (
                    float((predicted_good & actual_bad).sum() / actual_bad_count)
                    if actual_bad_count else float("nan")
                ),
                "false_bad_rate_among_good": (
                    float((~predicted_good & actual_good).sum() / actual_good_count)
                    if actual_good_count else float("nan")
                ),
            }
        )

    return pd.DataFrame(rows)
