
from __future__ import annotations

import streamlit as st

from fairlens.report import pct, render_markdown
from fairlens.ui import callout, header, setup_page, show_table, sidebar

setup_page("Findings and report")
sidebar()

header(
    "Findings and report",
    "What the evidence shows, what it does not, and where to look next. This page uses the final review you explicitly pinned.",
)

final_review = st.session_state.get("final_test_review")

if final_review is None:
    callout(
        "No final test review yet",
        "Explore the validation results first. When you are satisfied with a model and decision rule, open the Experiment lab "
        "and pin one final review. The test set is deliberately kept out of this report until then.",
        "caution",
    )
    st.page_link(
        "pages/4_Experiment_Lab.py",
        label="Go to the Experiment lab",
    )
    st.stop()

f = final_review["findings"]
t = f["test"]

st.caption(
    f"Pinned configuration: {final_review['model']} | {final_review['decision_rule']} | "
    f"held-out test set of {f['n_test']} applicants."
)

st.info(
    "This report is a frozen snapshot of the configuration you pinned. Changing the model or inputs in the sidebar "
    "does not change these results or trigger another test-set evaluation."
)

a, b, c, d = st.columns(4)
a.metric("Accuracy", pct(t["accuracy"]))
b.metric("Bad cases caught", pct(t["recall_other"]))
c.metric("Cost per applicant", f"{t['cost_per_applicant']:.2f}")
d.metric("All-Good baseline cost", f"{f['all_good']['cost_per_applicant']:.2f}")

st.subheader("What the evidence shows")

for line in f["observations"]:
    st.markdown(f"- {line}")

for line in f["cautions"]:
    st.warning(line)

st.subheader("Trade-offs to keep in mind")

st.markdown(
    "- Fewer costly mistakes usually means more good-risk applicants turned away.\n"
    "- A threshold that looks best on validation data can look different on new records.\n"
    "- Changing a threshold or removing an input can shrink one group gap and widen another. No single number settles fairness."
)

st.subheader("Limitations")

for line in f["limitations"]:
    st.markdown(f"- {line}")

st.subheader("Where to investigate next")

for line in f["next_steps"]:
    st.markdown(f"- {line}")

st.subheader("Take it with you")

report = render_markdown(f)

st.download_button(
    "Download the report (Markdown)",
    report,
    file_name="fairlens_report.md",
    mime="text/markdown",
    type="primary",
)

show_table(
    f["groups"][
        [
            "group",
            "sample_count",
            "predicted_good_rate",
            "false_good_rate_among_bad",
            "false_bad_rate_among_good",
        ]
    ].round(3)
)

st.caption(
    "The final test review is pinned for this app session. Citation and licence details are in the report."
)
