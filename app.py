from __future__ import annotations

import streamlit as st

from fairlens.config import dataset_path
from fairlens.ui import callout, card, demo_active, demo_banner, header, setup_page, sidebar

setup_page("Model review")
sidebar()  # keeps model choices alive while moving between pages

st.markdown(
    '<div class="fl-hero"><h2>See the decisions behind the model.</h2>'
    "<p>A model can be right most of the time and still make different mistakes for different people. FairLens lets you "
    "explore a credit-risk model applicant by applicant, map where outcomes diverge between age groups, test what really "
    "changes when you remove a sensitive input, and audit any model's decisions with your own file.</p></div>",
    unsafe_allow_html=True,
)
callout(
    "Educational, not operational",
    "This analyses a 1994 benchmark of historical credit-risk labels. It is not a lending tool or financial advice. "
    "A difference between groups is a reason to investigate; on its own it does not show discrimination or its cause.",
)

have_data = dataset_path().exists() or demo_active()
if not have_data:
    st.info("The dataset is not downloaded yet. Download it on the first page, or try everything now with clearly-labelled synthetic demo data.")
    if st.button("Try it now with synthetic demo data", type="primary"):
        st.session_state["use_demo_data"] = True
        st.rerun()
elif demo_active():
    demo_banner()

st.subheader("Hands-on tools")
tools = [
    ("pages/7_Applicant_Map.py", "Applicant map", "Every applicant as a dot, placed by similarity. Overlay a fairness terrain and click anyone to see why they were scored that way."),
    ("pages/8_Applicant_Simulator.py", "Applicant simulator", "Build a fictional applicant, watch the score move, and run what-if and twin tests on sensitive inputs."),
    ("pages/9_Proxy_Detector.py", "Proxy detector", "Can age be recovered from other inputs? Find out whether deleting a sensitive column actually removes it."),
    ("pages/10_Mitigation_Lab.py", "Mitigation lab", "Reweighing, input removal and threshold what-ifs compared on one trade-off map with honest uncertainty."),
    ("pages/11_Audit_Your_Model.py", "Audit your own model", "Upload any model's decisions and a group column for a transparent group comparison."),
]
cols = st.columns(3)
for k, (path, title, body) in enumerate(tools):
    with cols[k % 3]:
        card(title, body)
        st.page_link(path, label=f"Open {title.lower()}")
        st.write("")

st.subheader("A guided review in five steps")
steps = [
    ("Understand the data", "Where the records come from, what the labels mean, and who is represented."),
    ("Evaluate the model", "Compare simple baselines with two models and see which errors cost the most."),
    ("Investigate group outcomes", "Compare applicants under 25 with those 25 or older, always beside the number of people."),
    ("Experiment carefully", "Move the decision threshold on validation data and watch the trade-offs."),
    ("Review the findings", "A plain-language summary and a downloadable report, with limitations."),
]
html = "".join(f'<div class="fl-step"><b>{i}</b><div><strong>{t}</strong><br><span>{d}</span></div></div>' for i, (t, d) in enumerate(steps, start=1))
st.markdown(html, unsafe_allow_html=True)
st.write("")
st.page_link("pages/1_Understand_the_Data.py", label="Start the guided review" if have_data else "Go to the data page")
st.caption("Every figure in this app is computed from the loaded data. Synthetic demo data is always labelled as such.")
