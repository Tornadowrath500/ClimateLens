from __future__ import annotations

import streamlit as st

from fairlens.config import dataset_path
from fairlens.ui import callout, demo_active, demo_banner, setup_page, sidebar

setup_page("Overview")
sidebar()

st.markdown(
    '<div class="fl-hero"><h2>Understand credit model decisions.</h2>'
    "<p>Follow a clear review: learn what the data represents, inspect model errors, compare group outcomes, "
    "and explore how decision rules change the results.</p></div>",
    unsafe_allow_html=True,
)
callout(
    "Educational review only",
    "FairLens uses a small 1994 credit-risk benchmark. It is not a lending tool, a credit recommendation, "
    "or financial advice. Group differences are signals to investigate, not proof of discrimination or its cause.",
)

have_data = dataset_path().exists() or demo_active()
if not have_data:
    st.info("Choose how to begin. The benchmark download is available on the data page, or explore with clearly labelled synthetic data.")
    left, right = st.columns(2)
    with left:
        st.page_link("pages/1_Understand_the_Data.py", label="Understand the data", icon="📋", use_container_width=True)
    with right:
        if st.button("Explore synthetic demo", type="primary", use_container_width=True):
            st.session_state["use_demo_data"] = True
            st.rerun()
elif demo_active():
    demo_banner()

st.subheader("Choose a review stage")
st.caption("Each stage starts with a plain-language question. Detailed methods and definitions are available as you go.")
sections = [
    (
        "1 · Start with the evidence",
        "Check where the records came from and what the historical labels mean.",
        [("pages/1_Understand_the_Data.py", "Understand the data")],
    ),
    (
        "2 · Review model performance",
        "Compare models, inspect group outcomes, test decision changes, and save a findings snapshot.",
        [
            ("pages/2_Evaluate_the_Model.py", "Evaluate performance"),
            ("pages/3_Investigate_Group_Outcomes.py", "Compare group outcomes"),
            ("pages/4_Experiment_Lab.py", "Test decision changes"),
            ("pages/5_Findings_and_Report.py", "Findings and report"),
        ],
    ),
    (
        "3 · Explore individual applicants",
        "Use the interactive similarity map, inspect one profile, and examine possible proxy signals.",
        [
            ("pages/7_Applicant_Map.py", "Applicant map"),
            ("pages/8_Applicant_Simulator.py", "Applicant simulator"),
            ("pages/9_Proxy_Detector.py", "Proxy detector"),
        ],
    ),
    (
        "4 · Audit or improve a model",
        "Compare mitigation experiments or bring a CSV of model decisions for a transparent group audit.",
        [
            ("pages/10_Mitigation_Lab.py", "Mitigation lab"),
            ("pages/11_Audit_Your_Model.py", "Audit your own model"),
        ],
    ),
    (
        "5 · Check methods and limitations",
        "Review definitions, assumptions, sample sizes, and what the analysis cannot establish.",
        [("pages/6_Methodology_and_Limitations.py", "Methods and limits")],
    ),
]
for title, description, links in sections:
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.write(description)
        cols = st.columns(min(len(links), 4))
        for index, (path, label) in enumerate(links):
            cols[index % len(cols)].page_link(path, label=label, use_container_width=True)

st.caption("Every result is computed from the selected data. Synthetic demonstration results are identified on every page and report.")
