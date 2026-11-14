from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Methodology and limitations | FairLens", page_icon="◈", layout="wide")
st.title("Methodology and limitations")
st.subheader("What this project is")
st.write(
    "FairLens is an educational investigation of a historical classification benchmark. "
    "It is designed to help people understand model behavior, not to make real credit decisions."
)
st.subheader("What this project is not")
st.markdown(
    """
    - It is not a lending system, underwriting recommendation, or financial advice.
    - It does not establish whether a real institution discriminates.
    - It does not establish why a group difference occurs.
    - It does not establish that an observed model is suitable for current applicants.
    """
)
st.subheader("Data and evaluation commitments")
st.markdown(
    """
    - Cite the UCI source and retain its CC BY 4.0 attribution.
    - Keep local data files out of Git.
    - Separate training, validation, and final testing.
    - Never select models or thresholds based on final-test performance.
    - Document sample counts and uncertainty.
    - Explain failures and limits alongside favorable results.
    """
)
st.caption("Read docs/DATA_AND_ETHICS.md and docs/ROADMAP.md for the project contract.")
