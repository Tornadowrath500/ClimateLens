"""Proxy detection: can a sensitive attribute be recovered from the other inputs?"""

from __future__ import annotations

import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from fairlens.config import AGE_COLUMN, PERSONAL_STATUS_COLUMN, RANDOM_STATE, TARGET_COLUMN, feature_label
from fairlens.data import group_labels, make_age_groups
from fairlens.models import LOGISTIC, build_model


def _cv_auc(X: pd.DataFrame, y: pd.Series, folds: int = 5) -> float:
    cv = StratifiedKFold(folds, shuffle=True, random_state=RANDOM_STATE)
    p = cross_val_predict(build_model(LOGISTIC, X), X, y, cv=cv, method="predict_proba")[:, 1]
    return float(roc_auc_score(y, p))


def proxy_report(data: pd.DataFrame, drop_status: bool = False) -> dict:
    """AUC of predicting 'younger group' from everything except age (and optionally personal status).
    0.5 = no recoverable signal, 1.0 = perfectly recoverable. Cross-validated."""
    young, _ = group_labels()
    X = data.drop(columns=[TARGET_COLUMN, AGE_COLUMN] + ([PERSONAL_STATUS_COLUMN] if drop_status else []))
    y = (make_age_groups(data[AGE_COLUMN]) == young).astype(int)
    per = [{"column": c, "feature": feature_label(c), "auc": _cv_auc(X[[c]], y)} for c in X.columns]
    table = pd.DataFrame(per).sort_values("auc", ascending=False).reset_index(drop=True)
    return {"overall_auc": _cv_auc(X, y), "per_feature": table, "n_young": int(y.sum()), "n": int(len(y))}
