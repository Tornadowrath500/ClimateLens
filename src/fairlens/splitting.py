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
    strata: pd.Series | None = None,
) -> DatasetSplits:
    """Split into train/validation/test sets, preserving the proportions of `strata`.

    `strata` defaults to the target. Passing class x group labels keeps every
    group represented in every split, which matters for a small audit group.
    Validation is a fraction of the development set (after the test split), so
    the default is 64% train / 16% validation / 20% test.
    """
    if len(features) != len(target):
        raise ValueError("features and target must contain the same number of rows.")
    if not 0 < test_size < 1 or not 0 < validation_size < 1:
        raise ValueError("test_size and validation_size must both be between 0 and 1.")
    if not features.index.is_unique:
        raise ValueError("features must have a unique index.")

    labels = target if strata is None else pd.Series(strata, index=features.index)
    labels = pd.Series(labels.to_numpy(), index=features.index)

    X_dev, X_test, y_dev, y_test = train_test_split(
        features, target, test_size=test_size, random_state=random_state, stratify=labels
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_dev, y_dev, test_size=validation_size, random_state=random_state,
        stratify=labels.loc[X_dev.index],
    )
    return DatasetSplits(X_train, X_val, X_test, y_train, y_val, y_test)
