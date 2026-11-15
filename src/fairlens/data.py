"""Local dataset loading, validation and (explicit) download."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from fairlens.config import (
    AGE_COLUMN,
    AGE_GROUP_CUTOFF,
    CITATION,
    DATASET_PATH,
    MANIFEST_PATH,
    RAW_DATA_DIR,
    TARGET_COLUMN,
    UCI_URL,
    dataset_path,
)


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


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    """Load the locally downloaded benchmark and validate its schema."""
    file_path = Path(path) if path is not None else dataset_path()
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {file_path}. Run python scripts/download_dataset.py first."
        )
    frame = validate_dataset(pd.read_csv(file_path))
    frame[TARGET_COLUMN] = pd.to_numeric(frame[TARGET_COLUMN]).astype(int)
    return frame


def make_age_groups(age: pd.Series, cutoff: int = AGE_GROUP_CUTOFF) -> pd.Series:
    """Create the exploratory age grouping used for descriptive auditing."""
    values = pd.to_numeric(age, errors="raise")
    labels = [f"Under {cutoff}" if v < cutoff else f"{cutoff} or older" for v in values]
    return pd.Series(labels, index=age.index, name="age_group")


def group_labels(cutoff: int = AGE_GROUP_CUTOFF) -> tuple[str, str]:
    """(younger, older) group labels, matching make_age_groups."""
    return f"Under {cutoff}", f"{cutoff} or older"


def dataset_provenance(path: str | Path | None = None) -> dict:
    """Manifest written by the download script, or {} when unavailable."""
    manifest = MANIFEST_PATH if path is None else Path(path).with_name("dataset_manifest.json")
    try:
        return json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def benchmark_shape_warnings(frame: pd.DataFrame) -> list[str]:
    """Plain-language warnings when the file does not look like the UCI benchmark."""
    notes = []
    if len(frame) != 1000:
        notes.append(f"Expected 1,000 rows, found {len(frame):,}.")
    if frame.shape[1] - 1 != 20:
        notes.append(f"Expected 20 input features, found {frame.shape[1] - 1}.")
    return notes


def download_dataset(raw_dir: Path = RAW_DATA_DIR, *, output_path: Path | None = None) -> pd.DataFrame:
    """Explicitly download the UCI benchmark. Only ever called on a user's request.

    ``output_path`` supports local/offline-development overrides without writing
    the downloaded file somewhere different from the path the app will load.
    """
    from ucimlrepo import fetch_ucirepo  # imported lazily: only needed here

    raw_dir.mkdir(parents=True, exist_ok=True)
    dataset = fetch_ucirepo(id=144)
    features = dataset.data.features.copy()
    targets = dataset.data.targets.copy()
    if targets.shape[1] != 1:
        raise ValueError(f"Expected one target column; found {targets.shape[1]}.")

    target = pd.to_numeric(targets.iloc[:, 0], errors="raise").astype(int).rename(TARGET_COLUMN)
    frame = pd.concat([features.reset_index(drop=True), target.reset_index(drop=True)], axis=1)
    validate_dataset(frame)

    destination = Path(output_path) if output_path is not None else raw_dir / DATASET_PATH.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(destination, index=False)
    manifest = {
        "dataset": "Statlog (German Credit Data)",
        "uci_id": 144,
        "source": UCI_URL,
        "citation": CITATION,
        "license": "CC BY 4.0",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "rows": int(frame.shape[0]),
        "feature_count": int(features.shape[1]),
        "target_column": TARGET_COLUMN,
        "target_encoding": {"1": "Good", "2": "Bad"},
        "note": "Public UCI benchmark, shared under CC BY 4.0. Do not add private or user-supplied records.",
    }
    destination.with_name(MANIFEST_PATH.name).write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return frame

