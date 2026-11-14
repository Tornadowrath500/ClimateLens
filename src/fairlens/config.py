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


# ---- plain-language labels for the UCI codes (UCI data dictionary) ---------------------------------
VALUE_LABELS: dict[str, dict[str, str]] = {
    "Attribute1": {"A11": "Overdrawn (below 0 DM)", "A12": "Low balance (0 to 200 DM)", "A13": "Healthy (200+ DM or salary paid in)", "A14": "No checking account"},
    "Attribute3": {"A30": "No credits taken / all repaid", "A31": "All credits at this bank repaid", "A32": "Existing credits repaid on time", "A33": "Past delay in repaying", "A34": "Critical account / credits elsewhere"},
    "Attribute4": {"A40": "New car", "A41": "Used car", "A42": "Furniture / equipment", "A43": "Radio / TV", "A44": "Domestic appliances", "A45": "Repairs", "A46": "Education", "A47": "Vacation", "A48": "Retraining", "A49": "Business", "A410": "Other"},
    "Attribute6": {"A61": "Under 100 DM", "A62": "100 to 500 DM", "A63": "500 to 1000 DM", "A64": "1000+ DM", "A65": "Unknown / none"},
    "Attribute7": {"A71": "Unemployed", "A72": "Under 1 year", "A73": "1 to 4 years", "A74": "4 to 7 years", "A75": "7+ years"},
    "Attribute9": {"A91": "Male, divorced/separated", "A92": "Female, divorced/separated/married", "A93": "Male, single", "A94": "Male, married/widowed", "A95": "Female, single"},
    "Attribute10": {"A101": "None", "A102": "Co-applicant", "A103": "Guarantor"},
    "Attribute12": {"A121": "Real estate", "A122": "Savings agreement / life insurance", "A123": "Car or other", "A124": "Unknown / no property"},
    "Attribute14": {"A141": "Bank", "A142": "Stores", "A143": "None"},
    "Attribute15": {"A151": "Rent", "A152": "Own", "A153": "Free housing"},
    "Attribute17": {"A171": "Unskilled, non-resident", "A172": "Unskilled, resident", "A173": "Skilled employee", "A174": "Management / highly qualified"},
    "Attribute19": {"A191": "None", "A192": "Yes, registered"},
    "Attribute20": {"A201": "Yes", "A202": "No"},
}
SENSITIVE_COLUMNS = ("Attribute9", "Attribute13", "Attribute20")
# Inputs a person could plausibly change about a *request* (used for illustrative what-ifs only).
ACTIONABLE_COLUMNS = ("Attribute1", "Attribute2", "Attribute5", "Attribute6", "Attribute10", "Attribute14")


def feature_label(column: str) -> str:
    return FEATURE_DICTIONARY.get(column, (column,))[0]


def value_label(column: str, value) -> str:
    """Friendly text for a raw value; numbers and unknown codes pass through unchanged."""
    return VALUE_LABELS.get(column, {}).get(str(value), str(value))
