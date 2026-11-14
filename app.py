from __future__ import annotations

import streamlit as st

from fairlens.config import dataset_path
from fairlens.ui import callout, header, setup_page, sidebar

setup_page("Model review")
sidebar()  # keeps model choices alive while moving between pages

header(
    "Understand the decisions behind the model.",
    "A model can be right most of the time and still make different mistakes for different people. "
    "FairLens lets you see those mistakes, compare two age groups, and test what changes when the decision rule moves.",
)
callout(
    "Educational, not operational",
    "This analyses a 1994 benchmark of historical credit-risk labels. It is not a lending tool or financial advice. "
    "A difference between groups is a reason to investigate; on its own it does not show discrimination or its cause.",
)

st.subheader("A review in five steps")
steps = [
    ("Understand the data", "Where the records come from, what the labels mean, and who is represented."),
    ("Evaluate the model", "Compare simple baselines with two models and see which errors cost the most."),
    ("Investigate group outcomes", "Compare applicants under 25 with those 25 or older, always beside the number of people."),
    ("Experiment carefully", "Move the decision threshold on validation data and watch the trade-offs."),
    ("Review the findings", "A plain-language summary and a downloadable report, with limitations."),
]
html = "".join(f'<div class="fl-step"><b>{i}</b><div><strong>{t}</strong><br><span>{d}</span></div></div>'
               for i, (t, d) in enumerate(steps, start=1))
st.markdown(html, unsafe_allow_html=True)

st.write("")
if dataset_path().exists():
    st.page_link("pages/1_Understand_the_Data.py", label="Start with the data")
else:
    st.info("The dataset is not downloaded yet. The first page will offer to fetch it.")
    st.page_link("pages/1_Understand_the_Data.py", label="Go to the data page")
st.caption("Every figure in this app is computed from the downloaded data. Nothing is a placeholder.")
