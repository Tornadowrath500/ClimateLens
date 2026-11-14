from __future__ import annotations

import streamlit as st

from fairlens.config import DATASET_PATH
from fairlens.data import load_dataset, make_age_groups

st.set_page_config(page_title="Understand the data | FairLens", page_icon="◈", layout="wide")
st.title("Understand the data")
st.write("Start with the evidence: where the dataset came from, what it records, and who is represented.")

st.info(
    "Benchmark: UCI Statlog (German Credit Data), donated in 1994. "
    "It is a historical educational dataset, not a current picture of lending."
)

if not DATASET_PATH.exists():
    st.warning("No local dataset is present yet. Nothing has been downloaded automatically.")
    st.code("python scripts/download_dataset.py", language="bash")
    st.link_button(
        "Open the original UCI dataset page",
        "https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
    )
else:
    try:
        data = load_dataset()
    except Exception as exc:
        st.error(f"The local dataset could not be validated: {exc}")
    else:
        first, second, third = st.columns(3)
        first.metric("Rows", f"{len(data):,}")
        second.metric("Input features", f"{data.shape[1] - 1}")
        third.metric("Missing values", f"{int(data.isna().sum().sum()):,}")
        st.subheader("A sample of the data")
        st.dataframe(data.head(12), use_container_width=True, hide_index=True)
        st.subheader("Target labels")
        st.write("UCI defines 1 as Good and 2 as Bad. Keep the labels visible in analysis.")
        st.bar_chart(data["class"].value_counts().sort_index())
        st.subheader("Age groups used for exploratory comparison")
        st.write(
            "The initial exploratory split is under 25 versus 25 or older. "
            "This is an analysis choice, not a legal standard or proof of protected-group status."
        )
        groups = make_age_groups(data["Attribute13"])
        st.dataframe(groups.value_counts().rename_axis("Age group").reset_index(name="Applicants"), hide_index=True)

st.caption("Source and collection details: see docs/DATA_AND_ETHICS.md.")
