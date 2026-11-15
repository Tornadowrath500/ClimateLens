"""End-to-end audit: split, fit on train, score validation/test, repeat for stability."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from fairlens.baselines import predict_all_bad, predict_all_good
from fairlens.config import (
    AGE_COLUMN,
    AGE_GROUP_CUTOFF,
    BAD_RISK_LABEL,
    DEFAULT_THRESHOLD,
    GOOD_RISK_LABEL,
    RANDOM_STATE,
    TARGET_COLUMN,
)
from fairlens.data import group_labels, make_age_groups
from fairlens.metrics import (
    age_gap,
    classification_summary,
    group_outcome_metrics,
    predict_from_proba,
)
from fairlens.models import MODEL_NAMES, build_model, prob_good
from fairlens.splitting import DatasetSplits, stratified_split


@dataclass
class OperatingPoint:
    """The decision rule: one threshold for everyone, or separate ones per group."""

    threshold: float = DEFAULT_THRESHOLD
    per_group: dict[str, float] | None = None

    def apply(self, p_good, groups) -> np.ndarray:
        p = np.asarray(p_good, dtype=float)
        if not self.per_group:
            return predict_from_proba(p, self.threshold)
        g = np.asarray(pd.Series(groups, dtype="object").astype(str))
        limits = np.array([self.per_group.get(x, self.threshold) for x in g])
        return np.where(p >= limits, GOOD_RISK_LABEL, BAD_RISK_LABEL)

    def describe(self) -> str:
        if not self.per_group:
            return f"one threshold of {self.threshold:.2f} for everyone"
        parts = ", ".join(f"{k}: {v:.2f}" for k, v in sorted(self.per_group.items()))
        return f"separate thresholds ({parts})"


@dataclass
class Audit:
    """Fitted pipelines plus train/validation/test splits. Test scores are computed lazily."""

    seed: int
    excluded: tuple[str, ...]
    splits: DatasetSplits
    pipelines: dict
    _cache: dict = field(default_factory=dict)

    def _part(self, part: str):
        if part == "validation":
            return self.splits.X_validation, self.splits.y_validation
        if part == "test":
            return self.splits.X_test, self.splits.y_test
        raise ValueError("part must be 'validation' or 'test'.")

    def y(self, part: str) -> np.ndarray:
        return self._part(part)[1].to_numpy()

    def groups(self, part: str) -> np.ndarray:
        return make_age_groups(self._part(part)[0][AGE_COLUMN]).to_numpy()

    def proba(self, model_name: str, part: str) -> np.ndarray:
        key = (model_name, part)
        if key not in self._cache:
            self._cache[key] = prob_good(self.pipelines[model_name], self._part(part)[0])
        return self._cache[key]


def _strata(X: pd.DataFrame, y: pd.Series) -> pd.Series:
    return y.astype(str) + "|" + make_age_groups(X[AGE_COLUMN])


def run_audit(
    data: pd.DataFrame,
    excluded: tuple[str, ...] = (),
    seed: int = RANDOM_STATE,
    models: tuple[str, ...] = MODEL_NAMES,
) -> Audit:
    """Split (stratified on class x age group), then fit each candidate on the training set only."""
    X, y = data.drop(columns=[TARGET_COLUMN]), data[TARGET_COLUMN]
    splits = stratified_split(X, y, random_state=seed, strata=_strata(X, y))
    pipelines = {}
    for name in models:
        pipelines[name] = build_model(name, X, excluded).fit(splits.X_train, splits.y_train)
    return Audit(seed=seed, excluded=tuple(excluded), splits=splits, pipelines=pipelines)


def validation_comparison(audit: Audit, threshold: float = DEFAULT_THRESHOLD) -> pd.DataFrame:
    """Baselines and candidate models on the VALIDATION set at a fixed threshold."""
    y = audit.y("validation")
    rows = {
        "All-Good baseline": classification_summary(y, predict_all_good(len(y))),
        "All-Bad (reference only)": classification_summary(y, predict_all_bad(len(y))),
    }
    for name in audit.pipelines:
        p = audit.proba(name, "validation")
        rows[name] = classification_summary(y, predict_from_proba(p, threshold), p_good=p)
    table = pd.DataFrame(rows).T
    cols = ["accuracy", "balanced_accuracy", "precision", "recall", "f1", "auc", "cost_per_applicant"]
    return table[cols].astype(float).rename_axis("model").reset_index()


def repeat_split_gaps(
    data: pd.DataFrame,
    model_name: str,
    excluded: tuple[str, ...] = (),
    seeds=range(20),
    threshold: float = DEFAULT_THRESHOLD,
) -> pd.DataFrame:
    """Refit on many different splits to show how much an age-group gap moves by chance.

    Gaps are younger-minus-older on each repeated holdout sample, at one fixed threshold.
    """
    young, old = group_labels(AGE_GROUP_CUTOFF)
    X, y = data.drop(columns=[TARGET_COLUMN]), data[TARGET_COLUMN]
    rows = []
    for seed in seeds:
        splits = stratified_split(X, y, random_state=int(seed), strata=_strata(X, y))
        model = build_model(model_name, X, excluded).fit(splits.X_train, splits.y_train)
        p = prob_good(model, splits.X_test)
        pred = predict_from_proba(p, threshold)
        groups = make_age_groups(splits.X_test[AGE_COLUMN]).to_numpy()
        gaps = age_gap(group_outcome_metrics(splits.y_test.to_numpy(), pred, groups), young, old)
        summary = classification_summary(splits.y_test.to_numpy(), pred)
        rows.append(
            {
                "seed": int(seed),
                "predicted_good_gap": gaps["predicted_good_rate"],
                "false_good_gap": gaps["false_good_rate_among_bad"],
                "false_bad_gap": gaps["false_bad_rate_among_good"],
                "accuracy": summary["accuracy"],
                "cost_per_applicant": summary["cost_per_applicant"],
                "young_test_count": int((groups == young).sum()),
            }
        )
    return pd.DataFrame(rows)

