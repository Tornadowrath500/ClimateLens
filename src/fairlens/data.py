"""Local dataset loading and validation.

Downloading is intentionally separate; the UI must never fetch data silently.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from fairlens.config import AGE_COLUMN, DATASET_PATH, TARGET_COLUMN


def validate_dataset(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate the expected UCI benchmark schema without changing its values."""
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")
    if frame.empty:
        raise ValueError("The dataset is empty.")
    if TARGET_COLUMN not in frame.columns:
        raise ValueError(f"Expected target column {TARGET_COLUMN!r}.")
    if AGE_COLUMN not in frame.columns:
        raise ValueError(f"Expected age column {AGE_COLUMN!r} from the UCI data dictionary.")
    if frame[TARGET_COLUMN].isna().any():
        raise ValueError("The target column contains missing values.")

    labels = set(pd.to_numeric(frame[TARGET_COLUMN], errors="raise").unique())
    if labels != {1, 2}:
        raise ValueError(f"Expected target labels 1 (Good) and 2 (Bad); found {sorted(labels)}.")

    ages = pd.to_numeric(frame[AGE_COLUMN], errors="coerce")
    if ages.isna().any() or (ages <= 0).any():
        raise ValueError("The age column contains missing, nonnumeric, or nonpositive values.")

    return frame.copy()


def load_dataset(path: str | Path = DATASET_PATH) -> pd.DataFrame:
    """Load the locally downloaded benchmark and validate its schema."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {file_path}. Run python scripts/download_dataset.py first."
        )
    return validate_dataset(pd.read_csv(file_path))


def make_age_groups(age: pd.Series, cutoff: int = 25) -> pd.Series:
    """Create an explicitly exploratory age grouping for descriptive auditing."""
    values = pd.to_numeric(age, errors="raise")
    return pd.Series(
        values.map(lambda value: f"Under {cutoff}" if value < cutoff else f"{cutoff} or older"),
        index=age.index,
        name="age_group",
    )
