"""Model evaluation, group outcomes, repeated-split stability, the experiment lab and the pinned report."""

from __future__ import annotations

from datetime import datetime, timezone

from backend import state
from backend.errors import ServiceError
from backend.services.common import context, respond, source_info
from backend.services.content import DEMO_REPORT_HEADER
from fairlens.config import AGE_COLUMN, DEFAULT_THRESHOLD
from fairlens.data import group_labels
from fairlens.evaluation import OperatingPoint, repeat_split_gaps, validation_comparison
from fairlens.metrics import (
    best_threshold_by_cost, classification_summary, group_outcome_metrics, predict_from_proba,
    theoretical_cost_threshold, threshold_sweep,
)
from fairlens.models import MODEL_NAMES
from fairlens.report import compute_findings, compute_group_review, render_markdown

MAX_SPLITS = 50


# ---- page 2: evaluate the model ------------------------------------------------------------------
def evaluation_validation(source: str = "real", model: str = "Logistic regression", excluded=()) -> dict:
    ctx = context(source, model, excluded)
    table = validation_comparison(ctx.audit, DEFAULT_THRESHOLD)
    rows = table.set_index("model")
    y, p = ctx.audit.y("validation"), ctx.audit.proba(model, "validation")
    summary = classification_summary(y, predict_from_proba(p, DEFAULT_THRESHOLD), p_good=p)
    return respond(ctx, {
        "split": "validation", "threshold": DEFAULT_THRESHOLD, "n_validation": int(len(y)),
        "table": table,
        "best_model_by_auc": max(MODEL_NAMES, key=lambda m: rows.loc[m, "auc"]),
        "all_good_cost": rows.loc["All-Good baseline", "cost_per_applicant"],
        "all_bad_cost": rows.loc["All-Bad (reference only)", "cost_per_applicant"],
        "selected": summary,
    })


# ---- page 3: investigate group outcomes -----------------------------------------------------------
def groups_review(source: str = "real", model: str = "Logistic regression", excluded=(), decision_rule=None) -> dict:
    ctx = context(source, model, excluded, decision_rule)
    review = compute_group_review(ctx.audit, model, ctx.op, part="validation")
    return respond(ctx, {**review, "split": "validation", "group_labels": list(group_labels())})


def groups_stability(source: str = "real", model: str = "Logistic regression", excluded=(), n_splits: int = 30) -> dict:
    """Refit on n_splits stratified holdout splits (default 30, as before) and summarise the age-group gap."""
    if isinstance(n_splits, bool) or not isinstance(n_splits, int) or not 2 <= n_splits <= MAX_SPLITS:
        raise ServiceError(422, "invalid_n_splits", f"n_splits must be an integer from 2 to {MAX_SPLITS}.")
    ctx = context(source, model, excluded)
    young, _ = group_labels()
    configs = [("As configured", ctx.excluded)]
    if AGE_COLUMN not in ctx.excluded:
        configs.append(("Age removed from inputs", ctx.excluded + (AGE_COLUMN,)))
    runs = []
    for name, excl in configs:
        frame = repeat_split_gaps(ctx.data, model, excl, seeds=range(n_splits))
        gap = frame["predicted_good_gap"].dropna()
        runs.append({
            "name": name, "rows": frame,
            "summary": {"n": int(len(gap)), "median": gap.median() if len(gap) else None,
                        "min": gap.min() if len(gap) else None, "max": gap.max() if len(gap) else None,
                        "young_lower_count": int((gap < 0).sum())},
        })
    return respond(ctx, {"split": "test (repeated holdouts, sensitivity check only)", "n_splits": n_splits,
                         "young_label": young, "runs": runs})


# ---- page 4: experiment lab --------------------------------------------------------------------------
def _rates(summary: dict) -> dict:
    c = summary["confusion"]
    return {
        "predicted_good_rate": summary["predicted_good_rate"],
        "false_good_rate": c["bad_as_good"] / max(1, c["bad_as_good"] + c["bad_as_bad"]),
        "false_bad_rate": c["good_as_bad"] / max(1, c["good_as_bad"] + c["good_as_good"]),
        "cost_per_applicant": summary["cost_per_applicant"], "accuracy": summary["accuracy"],
    }


def experiment_sweep(source: str = "real", model: str = "Logistic regression", excluded=(), decision_rule=None) -> dict:
    ctx = context(source, model, excluded, decision_rule)
    y, g, p = ctx.audit.y("validation"), ctx.audit.groups("validation"), ctx.audit.proba(model, "validation")
    best_t, best_cost = best_threshold_by_cost(y, p)
    pred = ctx.op.apply(p, g)
    now = classification_summary(y, pred, p_good=p)
    base = classification_summary(y, OperatingPoint(DEFAULT_THRESHOLD).apply(p, g))
    return respond(ctx, {
        "split": "validation", "n_validation": int(len(y)),
        "best_threshold": best_t, "best_cost": best_cost, "theory_threshold": theoretical_cost_threshold(),
        "now": {**_rates(now), "summary": now}, "baseline": _rates(base),
        "group_metrics": group_outcome_metrics(y, pred, g),
        "sweep": threshold_sweep(y, p, g),
    })


def _review_view(review: dict) -> dict:
    return {
        "model": review["model"], "excluded": list(review["excluded"]), "decision_rule": review["decision_rule"],
        "pinned_at": review["pinned_at"], "findings": review["findings"],
    }


def experiment_pin(session_id: str | None, source: str = "real", model: str = "Logistic regression",
                   excluded=(), decision_rule=None) -> dict:
    """Pin the model + decision rule and run the one final test review for this session. Later calls get 409."""
    ctx = context(source, model, excluded, decision_rule)
    session = state.get_session(session_id)
    with session["lock"]:
        if session["pinned"] is not None:
            raise ServiceError(409, "test_review_already_pinned",
                               "A final test review is already pinned for this session and will not be recalculated.",
                               {"pinned": jsonable_view(session["pinned"])})
        session["pinned"] = {
            "model": model, "excluded": ctx.excluded, "decision_rule": ctx.op.describe(), "source": ctx.info,
            "pinned_at": datetime.now(timezone.utc).isoformat(), "findings": compute_findings(ctx.audit, model, ctx.op),
        }
        review = session["pinned"]
    return respond(review["source"], {"pinned": True, "review": _review_view(review)})


def jsonable_view(review: dict) -> dict:
    from backend.serialize import jsonable
    return jsonable(_review_view(review))


def experiment_pinned(session_id: str | None) -> dict:
    session = state.get_session(session_id)
    with session["lock"]:
        review = session["pinned"]
    if review is None:
        return respond(source_info("real"), {"pinned": False, "review": None})
    return respond(review["source"], {"pinned": True, "review": _review_view(review)})


# ---- page 5: findings and report -----------------------------------------------------------------
def report_findings(session_id: str | None) -> dict:
    out = experiment_pinned(session_id)
    if not out["pinned"]:
        raise ServiceError(404, "no_pinned_review",
                           "No final test review has been pinned in this session. Pin one in the Experiment lab first.")
    return out


def report_markdown(session_id: str | None) -> str:
    session = state.get_session(session_id)
    with session["lock"]:
        review = session["pinned"]
    if review is None:
        raise ServiceError(404, "no_pinned_review",
                           "No final test review has been pinned in this session. Pin one in the Experiment lab first.")
    text = render_markdown(review["findings"])
    return (DEMO_REPORT_HEADER + text) if review["source"]["synthetic"] else text
