from __future__ import annotations

import pandas as pd
import streamlit as st

from fairlens.config import AGE_COLUMN, AGE_GROUP_CUTOFF, FEATURE_DICTIONARY, TARGET_COLUMN, UCI_URL
from fairlens.data import make_age_groups
from fairlens.metrics import wilson_interval
from fairlens.ui import callout, header, provenance_note, require_data, setup_page, show_table, sidebar

setup_page("Understand the data")
sidebar()
header(
    "Understand the data",
    "Before judging any model, look at what it learns from: who is in the data, what the labels mean, and what is missing.",
)
data = require_data()

n, bad = len(data), int((data[TARGET_COLUMN] == 2).sum())
a, b, c = st.columns(3)
a.metric("Historical records", f"{n:,}")
b.metric("Input features", f"{data.shape[1] - 1}")
c.metric("Labelled Bad risk", f"{bad / n:.0%}", help=f"{bad} of {n} records carry label 2 (Bad).")

st.subheader("What the model is trying to predict")
st.write(
    "Each record is a past credit applicant with a label: **1 = Good risk** or **2 = Bad risk**. The model reads the 20 "
    "features and predicts the label. These are historical classifications, not what a lender approved, so a "
    "'Good' prediction here is called a favorable prediction, never an approval."
)
callout(
    "Two mistakes, very different costs",
    "The dataset's own cost matrix says calling a Bad-risk case Good costs <b>5</b>, while calling a Good-risk case Bad "
    "costs <b>1</b>. Every cost figure in this app uses that rule.",
    "caution",
)

st.subheader("The two age groups we compare")
st.write(
    f"We compare applicants under {AGE_GROUP_CUTOFF} with those {AGE_GROUP_CUTOFF} or older. This is an analysis "
    "choice made for exploration, not a legal category."
)
groups = make_age_groups(data[AGE_COLUMN])
columns = st.columns(2)
for col, name in zip(columns, sorted(groups.unique(), reverse=True)):
    part = data[groups == name]
    k = int((part[TARGET_COLUMN] == 2).sum())
    lo, hi = wilson_interval(k, len(part))
    with col:
        st.markdown(
            f'<div class="fl-group"><strong>{name}</strong><div class="n">{len(part):,} applicants</div>'
            f'{k} labelled Bad ({k / len(part):.0%}; plausible range {lo:.0%} to {hi:.0%})</div>',
            unsafe_allow_html=True,
        )
st.caption("A smaller group means noisier rates. Every later chart shows the group size next to each rate.")

st.subheader("What to keep in mind")
st.markdown(
    "- **Old and local.** The records were collected in Germany and donated in 1994.\n"
    "- **Labels are judgments.** Good and Bad were assigned by people and processes we cannot inspect.\n"
    "- **Sensitive fields are present.** Age, personal status and sex, and foreign-worker status are all features.\n"
    "- **Small data.** 1,000 records leave little room for conclusions about any subgroup."
)

with st.expander("Data dictionary: what each feature means"):
    rows = [{"Feature": k, "Meaning": v[0], "Type": v[1], "Description": v[2]} for k, v in FEATURE_DICTIONARY.items()]
    show_table(pd.DataFrame(rows))
with st.expander("Peek at the raw records"):
    show_table(data.head(10))

provenance_note(data)
st.caption(f"Source: [UCI Statlog (German Credit Data)]({UCI_URL}). More in docs/DATA_AND_ETHICS.md.")
