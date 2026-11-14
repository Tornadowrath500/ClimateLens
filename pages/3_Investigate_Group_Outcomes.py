from __future__ import annotations

import streamlit as st

from fairlens.config import AGE_COLUMN
from fairlens.evaluation import repeat_split_gaps
from fairlens.metrics import group_outcome_metrics
from fairlens.report import compute_group_review
from fairlens.ui import (
    OLD, YOUNG, callout, get_audit, get_op, group_rate_chart, header, require_data, setup_page, show_chart,
    show_table, sidebar, stability_chart,
)

setup_page("Investigate group outcomes")
settings = sidebar()
header(
    "Investigate group outcomes",
    "A model can behave differently for different groups. Here we make the differences visible and keep their uncertainty in view.",
)
data = require_data()
audit = get_audit(data, settings)
op = get_op()
findings = compute_group_review(audit, settings.model, op, part="validation")
metrics = findings["groups"]

st.caption(f"{settings.model} on the validation set. Decision rule: {op.describe()}. Change it in the Experiment lab.")
callout(
    "How to read this page",
    "Each line is a 95% Wilson confidence interval for its group rate under a binomial-sampling assumption. It describes "
    "sampling uncertainty; it is not a formal test of a difference or an explanation for one. The number beside each group "
    "is the denominator behind that rate. A difference is a signal to investigate, not proof of discrimination.",
)
show_chart(group_rate_chart(metrics))

st.subheader("What the numbers say")
for line in findings["group_observations"]:
    st.markdown(f"- {line}")
for line in findings["cautions"]:
    st.warning(line)

with st.expander("The counts behind every rate"):
    show_table(
        metrics[["group", "sample_count", "actual_bad_count", "actual_good_count", "predicted_good_count",
                 "false_good_count", "false_bad_count"]].rename(columns={
            "group": "Group", "sample_count": "Applicants", "actual_bad_count": "Labelled Bad",
            "actual_good_count": "Labelled Good", "predicted_good_count": "Classified Good",
            "false_good_count": "Bad classified Good", "false_bad_count": "Good classified Bad"})
    )

st.subheader("How stable is this gap?")
st.write(
    "One split can mislead. We refit on 30 repeated stratified holdout splits and record how the gap in the share classified Good "
    "moves at the default 0.50 threshold. This is a sensitivity check, not a way to select a final model. We also try "
    "removing age from the model's inputs, to see whether the gap depends on it."
)
key = (settings.model, settings.excluded)
if st.button("Run 30 different splits"):
    runs = {"As configured": repeat_split_gaps(data, settings.model, settings.excluded, seeds=range(30))}
    if AGE_COLUMN not in settings.excluded:
        runs["Age removed from inputs"] = repeat_split_gaps(
            data, settings.model, settings.excluded + (AGE_COLUMN,), seeds=range(30))
    st.session_state["stability"] = (key, runs)

saved = st.session_state.get("stability")
if saved and saved[0] == key:
    runs = saved[1]
    show_chart(stability_chart(runs))
    for name, frame in runs.items():
        gap = frame["predicted_good_gap"].dropna()
        lower = int((gap < 0).sum())
        st.markdown(
            f"- **{name}:** across {len(gap)} splits the typical (median) gap was {100 * gap.median():+.1f} points, "
            f"ranging from {100 * gap.min():+.1f} to {100 * gap.max():+.1f}. {YOUNG} were classified Good less often in "
            f"{lower} of {len(gap)} splits."
        )
    callout(
        "Reading it",
        "If the boxes straddle zero, the sign of the gap changes across these repeated holdout samples. If removing age "
        "barely moves the box, other features are carrying similar information. Neither result explains why a gap exists.",
    )
elif saved:
    st.info("Your model settings changed since the last run. Run the splits again to refresh this chart.")
