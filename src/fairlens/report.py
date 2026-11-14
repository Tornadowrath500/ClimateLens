"""Turn measured results into plain-language findings and a downloadable report.

Every number is computed from an Audit; nothing here is a placeholder. Wording
is deliberately descriptive: group differences are signals to investigate.
"""

from __future__ import annotations

import math
from datetime import date

from fairlens.baselines import predict_all_bad, predict_all_good
from fairlens.config import AGE_GROUP_CUTOFF, CITATION, COST_BAD_PREDICTED_GOOD, COST_GOOD_PREDICTED_BAD, UCI_URL
from fairlens.data import group_labels
from fairlens.evaluation import Audit, OperatingPoint
from fairlens.metrics import (
    age_gap,
    classification_summary,
    group_outcome_metrics,
    intervals_overlap,
    theoretical_cost_threshold,
)

SMALL_GROUP = 50
LIMITATIONS = [
    "The data are 1,000 historical records from a specific place and era; they do not describe current lending or today's applicants.",
    "Labels are historical Good/Bad risk classifications, not what a lender actually approved or what applicants actually did.",
    "The age split (under 25 vs 25 or older) is an analysis choice, not a legal standard, and ignores every other group.",
    "A group difference does not show discrimination, its cause, or legal unfairness; the data cannot separate these explanations.",
    "Subgroups are small, so rates are noisy; intervals and repeated splits show how much.",
    "Personal status and sex are bundled in one field, and age is a model input by default; removing inputs does not remove correlated proxies.",
    "This is an educational benchmark, not a lending system or financial advice.",
]
NEXT_STEPS = [
    "Repeat the audit on other splits and other age cut-offs and see which findings survive.",
    "Compare groups defined by sex or foreign-worker status, with the same denominators and intervals.",
    "Test calibration by group: does a predicted 80% mean the same thing in each group?",
    "Examine which features drive the model's disagreement between groups, and whether they are proxies.",
]


def pct(x: float, digits: int = 1) -> str:
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.{digits}f}%"


def _money(x: float) -> str:
    return f"{x:.2f}"


def compute_group_review(
    audit: Audit,
    model_name: str,
    op: OperatingPoint,
    *,
    part: str = "validation",
) -> dict:
    """Summarize age-group outcomes without touching the final test split by default.

    The validation split is intended for exploration. Pass ``part="test"`` only
    when creating the one-time, pinned final review.
    """
    if part not in {"validation", "test"}:
        raise ValueError("part must be 'validation' or 'test'.")

    young, old = group_labels(AGE_GROUP_CUTOFF)
    y = audit.y(part)
    groups_for_rows = audit.groups(part)
    probabilities = audit.proba(model_name, part)
    predictions = op.apply(probabilities, groups_for_rows)
    groups = group_outcome_metrics(y, predictions, groups_for_rows)
    table = groups.set_index("group")
    gaps = age_gap(groups, young, old)

    overlap = {}
    for key in ("predicted_good", "false_good", "false_bad"):
        try:
            overlap[key] = intervals_overlap(
                (table.loc[young, f"{key}_ci_low"], table.loc[young, f"{key}_ci_high"]),
                (table.loc[old, f"{key}_ci_low"], table.loc[old, f"{key}_ci_high"]),
            )
        except KeyError:
            overlap[key] = True

    n_young = int(table.loc[young, "sample_count"]) if young in table.index else 0
    n_old = int(table.loc[old, "sample_count"]) if old in table.index else 0
    observations = []
    if young in table.index and old in table.index:
        interval_note = (
            "The group-specific 95% intervals overlap; these descriptive intervals are not a formal test of a group difference."
            if overlap["predicted_good"] else
            "The group-specific 95% intervals do not overlap in this sample, a descriptive signal to investigate rather than an explanation."
        )
        observations.append(
            f"{young}: {pct(table.loc[young, 'predicted_good_rate'])} classified Good (n={n_young}); "
            f"{old}: {pct(table.loc[old, 'predicted_good_rate'])} (n={n_old}). {interval_note}"
        )
        observations.append(
            f"Among actually-Bad cases, {pct(table.loc[young, 'false_good_rate_among_bad'])} of {young} and "
            f"{pct(table.loc[old, 'false_good_rate_among_bad'])} of {old} were classified Good (the costly error); "
            f"among actually-Good cases, {pct(table.loc[young, 'false_bad_rate_among_good'])} and "
            f"{pct(table.loc[old, 'false_bad_rate_among_good'])} were classified Bad."
        )

    split_label = "validation" if part == "validation" else "held-out test"
    cautions = []
    if n_young < SMALL_GROUP:
        cautions.append(
            f"Only {n_young} {young} applicants are in this {split_label} sample, so every {young} rate is imprecise."
        )
    if n_old < SMALL_GROUP:
        cautions.append(
            f"Only {n_old} {old} applicants are in this {split_label} sample, so every {old} rate is imprecise."
        )
    if op.per_group:
        cautions.append(
            "Separate thresholds use age at decision time. That is a what-if experiment, not an endorsed or lawful practice."
        )

    return {
        "part": part,
        "groups": groups,
        "gaps": gaps,
        "overlap": overlap,
        "group_observations": observations,
        "cautions": cautions,
        "n_young": n_young,
        "n_old": n_old,
    }


def compute_findings(audit: Audit, model_name: str, op: OperatingPoint) -> dict:
    """Create the final report after the user deliberately pins a test review."""
    y_test, y_val = audit.y("test"), audit.y("validation")
    p_test, p_val = audit.proba(model_name, "test"), audit.proba(model_name, "validation")

    pred_test = op.apply(p_test, audit.groups("test"))
    pred_val = op.apply(p_val, audit.groups("validation"))
    test = classification_summary(y_test, pred_test, p_good=p_test)
    val = classification_summary(y_val, pred_val, p_good=p_val)
    all_good = classification_summary(y_test, predict_all_good(len(y_test)))
    all_bad = classification_summary(y_test, predict_all_bad(len(y_test)))
    group_review = compute_group_review(audit, model_name, op, part="test")
    groups = group_review["groups"]

    notes = [
        f"On {len(y_test)} held-out applicants the {model_name.lower()} classified {pct(test['accuracy'])} correctly, "
        f"against {pct(all_good['accuracy'])} for the all-Good baseline.",
        f"Under the UCI cost matrix (a Bad case classified Good costs {COST_BAD_PREDICTED_GOOD}, the reverse {COST_GOOD_PREDICTED_BAD}) "
        f"the model's average cost was {_money(test['cost_per_applicant'])} per applicant, versus "
        f"{_money(all_good['cost_per_applicant'])} for all-Good and {_money(all_bad['cost_per_applicant'])} for rejecting everyone.",
    ]
    if test["cost_per_applicant"] >= all_bad["cost_per_applicant"]:
        notes.append("Rejecting everyone would have cost less than this model: accuracy alone hides how lopsided the cost matrix is.")
    notes.extend(group_review["group_observations"])
    notes.append(
        f"Decision rule: {op.describe()}. Validation cost was {_money(val['cost_per_applicant'])} and test cost "
        f"{_money(test['cost_per_applicant'])}; any difference is the estimate shifting on new data."
    )

    return {
        "model": model_name,
        "decision_rule": op.describe(),
        "n_test": int(len(y_test)),
        "n_validation": int(len(y_val)),
        "n_train": int(len(audit.splits.y_train)),
        "excluded": audit.excluded,
        "seed": audit.seed,
        "test": test,
        "validation": val,
        "all_good": all_good,
        "all_bad": all_bad,
        "groups": groups,
        "gaps": group_review["gaps"],
        "overlap": group_review["overlap"],
        "theory_threshold": theoretical_cost_threshold(),
        "observations": notes,
        "group_observations": group_review["group_observations"],
        "cautions": group_review["cautions"],
        "limitations": LIMITATIONS,
        "next_steps": NEXT_STEPS,
    }

def render_markdown(f: dict) -> str:
    """One-page-style markdown audit report from compute_findings()."""
    t, g = f["test"], f["groups"]
    inputs_note = (
        "all 20 features" if not f["excluded"] else f"all features except {', '.join(f['excluded'])}"
    )
    lines = [
        "# FairLens audit report",
        f"*Generated {date.today().isoformat()}. Educational analysis of a historical benchmark, not a lending tool.*",
        "",
        "## Setup",
        f"- Data: UCI Statlog (German Credit) {UCI_URL}",
        f"- Model: {f['model']} using {inputs_note}; fitted on {f['n_train']} training records.",
        f"- Splits: {f['n_train']} train / {f['n_validation']} validation / {f['n_test']} test, stratified by class and age group (seed {f['seed']}).",
        f"- Decision rule: {f['decision_rule']}. Thresholds are chosen on validation data only; the test set is a final check.",
        "",
        "## Model performance (test set)",
        f"- Accuracy {pct(t['accuracy'])}; balanced accuracy {pct(t['balanced_accuracy'])}; AUC {t['auc']:.3f}.",
        f"- Good class: precision {pct(t['precision'])}, recall {pct(t['recall'])}, F1 {t['f1']:.3f}.",
        f"- Bad class: precision {pct(t['precision_other'])}, recall {pct(t['recall_other'])}.",
        f"- Cost per applicant: model {_money(t['cost_per_applicant'])}, all-Good {_money(f['all_good']['cost_per_applicant'])}, all-Bad {_money(f['all_bad']['cost_per_applicant'])}.",
        "",
        "## Group outcomes by age (test set)",
        "| Group | n | Classified Good (95% CI) | Bad cases classified Good | Good cases classified Bad |",
        "|---|---|---|---|---|",
    ]
    for _, r in g.iterrows():
        lines.append(
            f"| {r['group']} | {int(r['sample_count'])} "
            f"| {pct(r['predicted_good_rate'])} ({pct(r['predicted_good_ci_low'], 0)}-{pct(r['predicted_good_ci_high'], 0)}) "
            f"| {int(r['false_good_count'])}/{int(r['actual_bad_count'])} = {pct(r['false_good_rate_among_bad'])} "
            f"| {int(r['false_bad_count'])}/{int(r['actual_good_count'])} = {pct(r['false_bad_rate_among_good'])} |"
        )
    lines += ["", "## Observations"] + [f"- {x}" for x in f["observations"]]
    if f["cautions"]:
        lines += ["", "## Cautions for this run"] + [f"- {x}" for x in f["cautions"]]
    lines += ["", "## Limitations"] + [f"- {x}" for x in f["limitations"]]
    lines += ["", "## Where to investigate next"] + [f"- {x}" for x in f["next_steps"]]
    lines += ["", "## Citation", CITATION, ""]
    return "\n".join(lines)
