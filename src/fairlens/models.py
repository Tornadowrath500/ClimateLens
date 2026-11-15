"""Candidate model pipelines. Every transform is fitted on the training split only."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from pandas.api.types import is_numeric_dtype

from fairlens.config import GOOD_RISK_LABEL, RANDOM_STATE

LOGISTIC = "Logistic regression"
FOREST = "Random forest"
MODEL_NAMES = (LOGISTIC, FOREST)


def build_preprocessor(features: pd.DataFrame, exclude: tuple[str, ...] = ()) -> ColumnTransformer:
    """Scale numeric and one-hot encode categorical columns; `exclude` drops inputs."""
    kept = [c for c in features.columns if c not in exclude]
    numeric = [c for c in kept if is_numeric_dtype(features[c])]
    categorical = [c for c in kept if c not in numeric]
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_model(name: str, features: pd.DataFrame, exclude: tuple[str, ...] = ()) -> Pipeline:
    """One unfitted pipeline: preprocessing + classifier."""
    if name == LOGISTIC:
        estimator = LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)
    elif name == FOREST:
        estimator = RandomForestClassifier(
            n_estimators=300, min_samples_leaf=5, random_state=RANDOM_STATE, n_jobs=-1
        )
    else:
        raise ValueError(f"Unknown model {name!r}; choose from {MODEL_NAMES}.")
    return Pipeline([("preprocess", build_preprocessor(features, exclude)), ("model", estimator)])


def build_candidate_models(features: pd.DataFrame, exclude: tuple[str, ...] = ()) -> dict[str, Pipeline]:
    return {name: build_model(name, features, exclude) for name in MODEL_NAMES}


def prob_good(model: Pipeline, features: pd.DataFrame) -> np.ndarray:
    """Predicted probability of the Good-risk class (label 1), whatever the class order."""
    column = list(model.classes_).index(GOOD_RISK_LABEL)
    return model.predict_proba(features)[:, column]

