"""Service layer: all request logic, framework-agnostic. backend/api/* only adapts HTTP to these functions."""

from backend.services.applicants import map_applicant, map_build, simulator_evaluate, simulator_random, simulator_schema
from backend.services.byom import byom_audit, byom_sample, byom_upload
from backend.services.data import data_download, data_overview, data_status
from backend.services.evaluation import (
    evaluation_validation, experiment_pin, experiment_pinned, experiment_sweep, groups_review, groups_stability,
    report_findings, report_markdown,
)
from backend.services.fairness_tools import mitigation_run, proxies_removal, proxies_report
from backend.services.system import health, meta, methodology

__all__ = [n for n in dir() if not n.startswith("_")]
