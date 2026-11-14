"""Explicitly download the UCI German Credit benchmark to data/raw/."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from ucimlrepo import fetch_ucirepo

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DATA_PATH = RAW_DIR / "german_credit.csv"
MANIFEST_PATH = RAW_DIR / "dataset_manifest.json"


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dataset = fetch_ucirepo(id=144)
    features = dataset.data.features.copy()
    targets = dataset.data.targets.copy()

    if targets.shape[1] != 1:
        raise ValueError(f"Expected one target column; found {targets.shape[1]}.")

    target = pd.to_numeric(targets.iloc[:, 0], errors="raise").astype(int).rename("class")
    frame = pd.concat([features.reset_index(drop=True), target.reset_index(drop=True)], axis=1)

    if set(frame["class"].unique()) != {1, 2}:
        raise ValueError("Unexpected target encoding; expected 1 = Good and 2 = Bad.")

    frame.to_csv(DATA_PATH, index=False)
    manifest = {
        "dataset": "Statlog (German Credit Data)",
        "uci_id": 144,
        "source": "https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
        "citation": "Hofmann, H. (1994). Statlog (German Credit Data) [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5NC77.",
        "license": "CC BY 4.0",
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "rows": int(frame.shape[0]),
        "feature_count": int(features.shape[1]),
        "target_column": "class",
        "target_encoding": {"1": "Good", "2": "Bad"},
        "note": "Keep this local copy and manifest out of Git.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Saved {len(frame):,} rows and {features.shape[1]} features to {DATA_PATH}")
    print(frame["class"].value_counts().sort_index().rename(index={1: "Good (1)", 2: "Bad (2)"}))


if __name__ == "__main__":
    main()
