"""Shared configuration and verified benchmark label definitions."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DATASET_PATH = RAW_DATA_DIR / "german_credit.csv"
MANIFEST_PATH = RAW_DATA_DIR / "dataset_manifest.json"

TARGET_COLUMN = "class"
AGE_COLUMN = "Attribute13"
GOOD_RISK_LABEL = 1
BAD_RISK_LABEL = 2
AGE_GROUP_CUTOFF = 25
RANDOM_STATE = 42
