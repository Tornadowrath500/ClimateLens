from __future__ import annotations

import streamlit as st

from fairlens.config import DEFAULT_THRESHOLD
from fairlens.evaluation import OperatingPoint
from fairlens.metrics import (
    best_threshold_by_cost, classification_summary, group_outcome_metrics, theoretical_cost_threshold, threshold_sweep,
)
from fairlens.report import compute_findings, pct
from fairlens.ui import (
    OLD, YOUNG, callout, get_audit, get_op, group_rate_chart, header, require_data, set_op, setup_page, show_chart,
    sidebar, sweep_chart,
)

setup_page("Experiment lab")
settings = sidebar()
header(
    "Experiment lab",
    "Move the decision threshold and watch what changes: the errors, the cost, and the outcomes for each age group.",
)
data = require_data()
audit = get_audit(data, settings)
y, g, p = audit.y("validation"), audit.groups("validation"), audit.proba(settings.model, "validation")

callout(
    "Why a threshold matters",
    "The model gives each applicant a probability of being Good. A threshold turns that into a decision: classify Good "
    "when the probability is at least the threshold. Raising it makes the model more cautious. "
    "Everything on this page uses the <b>validation set</b>; the test set stays untouched until you choose to check.",
)
best_t, best_cost = best_threshold_by_cost(y, p)
theory = theoretical_cost_threshold()

mode = st.radio("Decision rule", ["One threshold for everyone", "Different thresholds by age group (what-if)"],
                horizontal=True, key="lab_mode")
if mode.startswith("One"):
    st.button("Jump to the best threshold on validation data", on_click=lambda: st.session_state.update(lab_t=best_t))
    t = st.slider("Threshold", 0.05, 0.95, DEFAULT_THRESHOLD, 0.01, key="lab_t")
    op, marks = OperatingPoint(t), {"Your setting": t}
else:
    c1, c2 = st.columns(2)
    ty = c1.slider(f"Threshold: {YOUNG}", 0.05, 0.95, DEFAULT_THRESHOLD, 0.01, key="lab_t_young")
    to = c2.slider(f"Threshold: {OLD}", 0.05, 0.95, DEFAULT_THRESHOLD, 0.01, key="lab_t_old")
    op, marks = OperatingPoint(DEFAULT_THRESHOLD, {YOUNG: ty, OLD: to}), {}
    st.warning(
        "Using age to set different cut-offs is a what-if experiment, not a recommendation. Treating groups differently "
        "when deciding can itself raise legal and ethical concerns."
    )
marks |= {"Best on validation": best_t, "Theory (5/6)": theory}

now = classification_summary(y, op.apply(p, g), p_good=p)
base = classification_summary(y, OperatingPoint(DEFAULT_THRESHOLD).apply(p, g))
fg = lambda s: s["confusion"]["bad_as_good"] / max(1, s["confusion"]["bad_as_good"] + s["confusion"]["bad_as_bad"])
fb = lambda s: s["confusion"]["good_as_bad"] / max(1, s["confusion"]["good_as_bad"] + s["confusion"]["good_as_good"])
a, b, c, d = st.columns(4)
a.metric("Classified Good", pct(now["predicted_good_rate"]), f"{100 * (now['predicted_good_rate'] - base['predicted_good_rate']):+.1f} pts vs 0.50", delta_color="off")
b.metric("Bad cases classified Good", pct(fg(now)), f"{100 * (fg(now) - fg(base)):+.1f} pts", delta_color="inverse",
         help="The costly mistake: each one costs 5.")
c.metric("Good cases classified Bad", pct(fb(now)), f"{100 * (fb(now) - fb(base)):+.1f} pts", delta_color="inverse",
         help="The cheaper mistake: each one costs 1.")
d.metric("Cost per applicant", f"{now['cost_per_applicant']:.2f}", f"{now['cost_per_applicant'] - base['cost_per_applicant']:+.2f}",
         delta_color="inverse", help="Average UCI cost. Lower is better.")
st.caption(f"Validation set, {len(y)} applicants. Changes are measured against the default threshold of 0.50.")

show_chart(group_rate_chart(group_outcome_metrics(y, op.apply(p, g), g)))
show_chart(sweep_chart(threshold_sweep(y, p, g), marks))
with st.expander("Why is the best threshold so high?"):
    st.write(
        f"A Bad case called Good costs five times a Good case called Bad. If the probabilities were perfectly calibrated, "
        f"calling Good only pays off above 5/6, about {theory:.2f}. On this validation set the lowest cost is at "
        f"{best_t:.2f} (cost {best_cost:.2f}); with only {len(y)} applicants that number is noisy, which is why the test check below matters."
    )

st.subheader("One final check on the held-out test set")
st.write(
    "After exploring on validation data, pin your model and decision rule to unlock one final test review for this session. "
    "The result is saved as a fixed snapshot; changing settings afterward will not rerun the test."
)
final_review = st.session_state.get("final_test_review")
if final_review is None:
    if st.button("Pin this setting and use the final test review", type="primary"):
        findings = compute_findings(audit, settings.model, op)
        st.session_state["final_test_review"] = {
            "findings": findings,
            "model": settings.model,
            "excluded": settings.excluded,
            "decision_rule": op.describe(),
        }
        st.session_state["test_looks"] = 1
        st.rerun()
    st.caption("No final test review has been run in this session.")
else:
    findings = final_review["findings"]
    st.success("The final test review is pinned. It will not be recalculated during this session.")
    st.markdown(
        f"**Pinned configuration:** {final_review['model']} using "
        f"{', '.join(final_review['excluded']) if final_review['excluded'] else 'all features'}; "
        f"{final_review['decision_rule']}."
    )
    x, y2, z = st.columns(3)
    x.metric("Cost per applicant: validation", f"{findings['validation']['cost_per_applicant']:.2f}")
    y2.metric("Cost per applicant: test", f"{findings['test']['cost_per_applicant']:.2f}")
    z.metric("Test accuracy", pct(findings["test"]["accuracy"]))
    st.info(
        "A difference between validation and test cost is the estimate shifting on new records. "
        "Threshold changes do not make a model fair by themselves."
    )
    for line in findings["cautions"]:
        st.warning(line)
    st.page_link("pages/5_Findings_and_Report.py", label="See the pinned findings and report")
