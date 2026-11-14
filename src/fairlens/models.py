"""Candidate model pipelines; fit only on the training split."""

from __future__ import annotations

from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from fairlens.config import RANDOM_STATE


def build_preprocessor() -> ColumnTransformer:
    """Build preprocessing based on column dtypes, fit only within each pipeline."""
    numeric = Pipeline(steps=[("scale", StandardScaler())])
    categorical = Pipeline(steps=[("encode", OneHotEncoder(handle_unknown="ignore"))])

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric, make_column_selector(dtype_include="number")),
            ("categorical", categorical, make_column_selector(dtype_exclude="number")),
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )


def build_candidate_models() -> dict[str, Pipeline]:
    """Return a compact starting set for validation comparison."""
    return {
        "Logistic regression": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
            ]
        ),
        "Random forest": Pipeline(
            steps=[
                ("preprocess", build_preprocessor()),
                (
                    "model",
                    RandomForestClassifier(
                        n_estimators=300,
                        min_samples_leaf=5,
                        random_state=RANDOM_STATE,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }
