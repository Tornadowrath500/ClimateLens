"""App metadata: constants, the data dictionary and plain-language definitions the frontend needs."""

from __future__ import annotations

from backend import state
from backend.errors import ServiceError
from backend.serialize import jsonable
from backend.services.common import TOGGLEABLE_INPUTS
from backend.services.content import METRIC_HELP
from fairlens import __version__ as core_version
from fairlens.config import (
    ACTIONABLE_COLUMNS, AGE_COLUMN, AGE_GROUP_CUTOFF, CITATION, COST_BAD_PREDICTED_GOOD, COST_GOOD_PREDICTED_BAD,
    DEFAULT_THRESHOLD, FEATURE_DICTIONARY, PERSONAL_STATUS_COLUMN, RANDOM_STATE, SENSITIVE_COLUMNS, TARGET_COLUMN,
    UCI_URL, VALUE_LABELS,
)
from fairlens.data import group_labels
from fairlens.metrics import DEFAULT_GRID, theoretical_cost_threshold
from fairlens.models import MODEL_NAMES
from fairlens.report import LIMITATIONS, NEXT_STEPS

API_VERSION = "1.0"


def health() -> dict:
    return {"status": "ok", "api_version": API_VERSION, "core_version": core_version}


def meta() -> dict:
    young, old = group_labels()
    features = [
        {
            "column": col, "label": label, "type": kind, "description": desc,
            "sensitive": col in SENSITIVE_COLUMNS,
            "values": [{"value": code, "label": text} for code, text in VALUE_LABELS.get(col, {}).items()],
        }
        for col, (label, kind, desc) in FEATURE_DICTIONARY.items()
    ]
    return jsonable({
        "api_version": API_VERSION,
        "models": list(MODEL_NAMES),
        "target_column": TARGET_COLUMN,
        "age_column": AGE_COLUMN,
        "personal_status_column": PERSONAL_STATUS_COLUMN,
        "toggleable_inputs": [
            {"column": AGE_COLUMN, "label": "Age"},
            {"column": PERSONAL_STATUS_COLUMN, "label": "Personal status and sex"},
        ],
        "age_group_cutoff": AGE_GROUP_CUTOFF,
        "groups": {"young": young, "old": old},
        "costs": {"bad_predicted_good": COST_BAD_PREDICTED_GOOD, "good_predicted_bad": COST_GOOD_PREDICTED_BAD},
        "default_threshold": DEFAULT_THRESHOLD,
        "theory_threshold": theoretical_cost_threshold(),
        "threshold_range": {"min": float(DEFAULT_GRID[0]), "max": float(DEFAULT_GRID[-1]), "step": 0.01},
        "random_state": RANDOM_STATE,
        "sensitive_columns": list(SENSITIVE_COLUMNS),
        "actionable_columns": list(ACTIONABLE_COLUMNS),
        "features": features,
        "metric_help": METRIC_HELP,
        "limitations": LIMITATIONS,
        "next_steps": NEXT_STEPS,
        "citation": CITATION,
        "uci_url": UCI_URL,
        "split": {"train": 0.64, "validation": 0.16, "test": 0.20},
    })


def methodology(source: str = "real") -> dict:
    """Constants for the methodology page, plus actual split sizes when a dataset is available."""
    sizes = None
    try:
        audit, _ = state.get_audit(source, ())
        s = audit.splits
        sizes = {"train": len(s.y_train), "validation": len(s.y_validation), "test": len(s.y_test)}
    except ServiceError:
        pass
    return jsonable({
        "costs": {"bad_predicted_good": COST_BAD_PREDICTED_GOOD, "good_predicted_bad": COST_GOOD_PREDICTED_BAD},
        "split_sizes": sizes, "limitations": LIMITATIONS, "citation": CITATION,
    })