"""Shared validation and context helpers for every service. No web-framework imports here."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from backend import state
from backend.errors import ServiceError
from backend.serialize import jsonable
from backend.services.content import DEMO_NOTICE
from fairlens.config import AGE_COLUMN, DEFAULT_THRESHOLD, PERSONAL_STATUS_COLUMN
from fairlens.data import group_labels
from fairlens.evaluation import Audit, OperatingPoint
from fairlens.models import MODEL_NAMES

TOGGLEABLE_INPUTS = (AGE_COLUMN, PERSONAL_STATUS_COLUMN)  # the two inputs the sidebar can switch off


def source_info(source: str) -> dict:
    if source == "demo":
        return {"kind": "demo", "synthetic": True, "label": "SYNTHETIC DEMO DATA", "notice": DEMO_NOTICE}
    return {"kind": "real", "synthetic": False, "label": "UCI Statlog (German Credit)", "notice": None}


def check_model(model: str) -> str:
    if model not in MODEL_NAMES:
        raise ServiceError(422, "invalid_model", f"Unknown model {model!r}.", {"allowed": list(MODEL_NAMES)})
    return model


def canon_excluded(excluded) -> tuple[str, ...]:
    """Validated, de-duplicated, in the fixed order the Streamlit sidebar used (age, then personal status)."""
    wanted = set(excluded or ())
    bad = wanted - set(TOGGLEABLE_INPUTS)
    if bad:
        raise ServiceError(422, "invalid_excluded", "Only age and personal status can be switched off.",
                           {"allowed": list(TOGGLEABLE_INPUTS), "received": sorted(bad)})
    return tuple(c for c in TOGGLEABLE_INPUTS if c in wanted)


def _unit_float(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not 0.0 <= float(value) <= 1.0:
        raise ServiceError(422, "invalid_decision_rule", f"{name} must be a number between 0 and 1.")
    return float(value)


def parse_rule(rule: dict | None) -> OperatingPoint:
    """{'threshold': 0.5, 'per_group': {'Under 25': 0.4, '25 or older': 0.5} | None} -> OperatingPoint."""
    rule = rule or {}
    unknown = set(rule) - {"threshold", "per_group"}
    if unknown:
        raise ServiceError(422, "invalid_decision_rule", f"Unknown decision_rule fields: {sorted(unknown)}.")
    threshold = _unit_float(rule.get("threshold", DEFAULT_THRESHOLD), "threshold")
    per_group = rule.get("per_group")
    if per_group:
        allowed = set(group_labels())
        if not isinstance(per_group, dict) or set(per_group) - allowed:
            raise ServiceError(422, "invalid_decision_rule", "per_group keys must be the two age-group labels.",
                               {"allowed": sorted(allowed)})
        per_group = {k: _unit_float(v, f"per_group[{k}]") for k, v in per_group.items()}
    return OperatingPoint(threshold, per_group or None)


def rule_dict(op: OperatingPoint) -> dict:
    return {"threshold": op.threshold, "per_group": op.per_group, "description": op.describe()}


@dataclass
class Context:
    source: str
    model: str
    excluded: tuple[str, ...]
    op: OperatingPoint
    data: pd.DataFrame
    audit: Audit
    audit_key: tuple
    info: dict

    def settings(self) -> dict:
        return {"model": self.model, "excluded": list(self.excluded), "decision_rule": rule_dict(self.op)}


def context(source: str, model: str, excluded, decision_rule: dict | None = None) -> Context:
    check_model(model)
    excluded = canon_excluded(excluded)
    op = parse_rule(decision_rule)
    data, _ = state.get_dataset(source)
    audit, akey = state.get_audit(source, excluded)
    return Context(source, model, excluded, op, data, audit, akey, source_info(source))


def respond(ctx_or_info, payload: dict) -> dict:
    """Standard envelope: the payload plus data_source (so every page can label synthetic data) and settings."""
    if isinstance(ctx_or_info, Context):
        payload = {**payload, "data_source": ctx_or_info.info, "settings": ctx_or_info.settings()}
    else:
        payload = {**payload, "data_source": ctx_or_info}
    return jsonable(payload)
