"""Reproducible stratified splits for the static classification benchmark."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

from fairlens.config import RANDOM_STATE


@dataclass(frozen=True)
class DatasetSplits:
    X_train: pd.DataFrame
    X_validation: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_validation: pd.Series
    y_test: pd.Series


def stratified_split(
    features: pd.DataFrame,
    target: pd.Series,
    *,
    test_size: float = 0.20,
    validation_size: float = 0.20,
    random_state: int = RANDOM_STATE,
) -> DatasetSplits:
    """Split into train/validation/test sets while preserving class proportions."""
    if len(features) != len(target):
        raise ValueError("features and target must contain the same number of rows.")
    if not 0 < test_size < 1 or not 0 < validation_size < 1:
        raise ValueError("test_size and validation_size must both be between 0 and 1.")

    X_development, X_test, y_development, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )
    X_train, X_validation, y_train, y_validation = train_test_split(
        X_development,
        y_development,
        test_size=validation_size,
        random_state=random_state,
        stratify=y_development,
    )

    return DatasetSplits(
        X_train=X_train,
        X_validation=X_validation,
        X_test=X_test,
        y_train=y_train,
        y_validation=y_validation,
        y_test=y_test,
    )
