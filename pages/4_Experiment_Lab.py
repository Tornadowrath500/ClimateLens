from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Experiment lab | FairLens", page_icon="◈", layout="wide")
st.title("Experiment lab")
st.write("Explore the consequences of changing a model decision rule. An experiment is not automatically an improvement.")

st.subheader("Planned investigation")
st.markdown(
    """
    1. Select a model that has already been chosen using validation data.
    2. Adjust its decision threshold using validation data only.
    3. Compare predicted-Good rates and error rates across groups.
    4. Show the associated cost trade-offs.
    5. Keep the final test set untouched until the analysis design is fixed.
    """
)
st.info(
    "The interactive threshold simulator and mitigation experiments have not been implemented yet. "
    "They will be added only after the baseline and evaluation pipeline are reliable."
)
