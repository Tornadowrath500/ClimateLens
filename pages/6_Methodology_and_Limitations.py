from __future__ import annotations

import streamlit as st

from fairlens.config import CITATION, COST_BAD_PREDICTED_GOOD, COST_GOOD_PREDICTED_BAD, dataset_path
from fairlens.ui import callout, header, require_data, setup_page, sidebar

setup_page("Methodology and limitations")
settings = sidebar()
header("Methodology and limitations", "How the numbers are made, and what they cannot tell you.")

callout(
    "What this project is not",
    "It is not a lending system, underwriting advice or financial advice. It does not establish whether any real "
    "institution discriminates, why a group difference occurs, or that a model suits today's applicants.",
    "caution",
)
st.subheader("How the evaluation works")
st.markdown(
    "- **Data:** UCI Statlog (German Credit), 1,000 records, 20 features. Target 1 = Good, 2 = Bad, verified on load.\n"
    "- **Splits:** stratified by class and age group, 64% train, 16% validation, 20% test, with a fixed random seed.\n"
    "- **Leakage control:** scaling and encoding live inside a scikit-learn Pipeline and are fitted on training data only.\n"
    "- **Selection:** models are compared and thresholds chosen on validation data. The final test set stays hidden until "
    "you pin one review per app session; that report remains fixed afterward.\n"
    f"- **Cost:** a Bad case predicted Good costs {COST_BAD_PREDICTED_GOOD}; a Good case predicted Bad costs {COST_GOOD_PREDICTED_BAD} (UCI matrix).\n"
    "- **Uncertainty:** 95% Wilson intervals on every group rate, plus repeated random splits for stability."
)
if dataset_path().exists():
    data = require_data()
    from fairlens.ui import get_audit
    s = get_audit(data, settings).splits
    st.caption(f"Current split sizes: {len(s.y_train)} train, {len(s.y_validation)} validation, {len(s.y_test)} test.")

st.subheader("Metric definitions")
st.markdown(
    "- **Classified Good rate:** classified Good / all applicants in the group. A proxy for a favorable prediction, not an approval rate.\n"
    "- **Bad cases classified Good:** labelled Bad and classified Good / all labelled Bad in the group.\n"
    "- **Good cases classified Bad:** labelled Good and classified Bad / all labelled Good in the group.\n"
    "- **Cost per applicant:** (5 x Bad-as-Good + 1 x Good-as-Bad) / applicants."
)
st.subheader("Limitations")
from fairlens.report import LIMITATIONS
for line in LIMITATIONS:
    st.markdown(f"- {line}")
st.subheader("Credits")
st.markdown(
    f"- Data: {CITATION}\n- Libraries: Streamlit, pandas, NumPy, scikit-learn, Plotly.\n"
    "- AI assistance: this application was developed with help from AI coding assistants; all results are computed from the data."
)
st.caption("Fuller project contract: docs/DATA_AND_ETHICS.md and docs/ROADMAP.md.")
