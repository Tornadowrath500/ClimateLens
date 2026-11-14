from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Investigate group outcomes | FairLens", page_icon="◈", layout="wide")
st.title("Investigate group outcomes")
st.write("A model can perform differently across groups. The goal here is to make those differences visible and interpretable.")

st.subheader("First comparison: age")
st.write(
    "The initial exploratory grouping is under 25 versus 25 or older. "
    "Always show the number of applicants in each group next to a rate."
)
st.subheader("Measures planned")
st.markdown(
    """
    - **Predicted-Good rate:** a proxy for the share receiving a favorable model classification; it is not an actual loan approval rate.
    - **False-Good rate among actually Bad cases:** the share of bad-risk labels predicted as Good.
    - **False-Bad rate among actually Good cases:** the share of good-risk labels predicted as Bad.
    - **Group sample count:** essential context for interpreting every rate.
    """
)
st.warning(
    "A difference between groups is a descriptive finding, not proof of discrimination, "
    "causation, or legal noncompliance. Small groups and this dataset's age require particular caution."
)
st.info("The group comparison module is scaffolded but has not yet been connected to trained predictions.")
