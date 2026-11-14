"""Shared configuration and verified benchmark definitions."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DATASET_PATH = RAW_DATA_DIR / "german_credit.csv"
MANIFEST_PATH = RAW_DATA_DIR / "dataset_manifest.json"
DATA_PATH_ENV = "FAIRLENS_DATA_PATH"  # optional override, e.g. for offline development

UCI_URL = "https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data"
CITATION = (
    "Hofmann, H. (1994). Statlog (German Credit Data) [Dataset]. "
    "UCI Machine Learning Repository. https://doi.org/10.24432/C5NC77 (CC BY 4.0)"
)

TARGET_COLUMN = "class"
AGE_COLUMN = "Attribute13"
PERSONAL_STATUS_COLUMN = "Attribute9"  # UCI: personal status AND sex combined
GOOD_RISK_LABEL = 1
BAD_RISK_LABEL = 2
AGE_GROUP_CUTOFF = 25
RANDOM_STATE = 42
DEFAULT_THRESHOLD = 0.5

# UCI cost matrix: an actually-Bad case predicted Good costs 5; the reverse costs 1.
COST_BAD_PREDICTED_GOOD = 5
COST_GOOD_PREDICTED_BAD = 1

# (plain-language name, type, description) from the UCI data dictionary.
FEATURE_DICTIONARY: dict[str, tuple[str, str, str]] = {
    "Attribute1": ("Checking account status", "categorical", "State of the applicant's existing checking account."),
    "Attribute2": ("Duration (months)", "numeric", "Length of the requested credit."),
    "Attribute3": ("Credit history", "categorical", "How earlier credits were repaid."),
    "Attribute4": ("Purpose", "categorical", "What the credit is for (car, furniture, education, ...)."),
    "Attribute5": ("Credit amount", "numeric", "Size of the requested credit."),
    "Attribute6": ("Savings account / bonds", "categorical", "Savings held by the applicant."),
    "Attribute7": ("Present employment", "categorical", "How long the applicant has been in their current job."),
    "Attribute8": ("Installment rate", "numeric", "Installment as a percentage of disposable income."),
    "Attribute9": ("Personal status and sex", "categorical", "Marital status and sex, combined in one field (sensitive)."),
    "Attribute10": ("Other debtors / guarantors", "categorical", "Whether another party is involved in the credit."),
    "Attribute11": ("Residence duration", "numeric", "Years at the present residence."),
    "Attribute12": ("Property", "categorical", "Most valuable property the applicant owns."),
    "Attribute13": ("Age (years)", "numeric", "Age of the applicant (used for the group audit)."),
    "Attribute14": ("Other installment plans", "categorical", "Credit commitments at banks or stores."),
    "Attribute15": ("Housing", "categorical", "Rent, own, or free housing."),
    "Attribute16": ("Existing credits", "numeric", "Number of existing credits at this bank."),
    "Attribute17": ("Job", "categorical", "Skill level and type of employment."),
    "Attribute18": ("People liable for maintenance", "numeric", "Number of people the applicant supports."),
    "Attribute19": ("Telephone", "categorical", "Whether a telephone is registered to the applicant."),
    "Attribute20": ("Foreign worker", "categorical", "Whether the applicant is a foreign worker (sensitive)."),
}


def dataset_path() -> Path:
    """Dataset location; FAIRLENS_DATA_PATH overrides the default."""
    override = os.environ.get(DATA_PATH_ENV)
    return Path(override) if override else DATASET_PATH
