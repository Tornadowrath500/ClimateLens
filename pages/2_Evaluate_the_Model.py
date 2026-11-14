from __future__ import annotations

import streamlit as st

from fairlens.config import GOOD_RISK_LABEL, BAD_RISK_LABEL

st.set_page_config(page_title="Evaluate the model | FairLens", page_icon="◈", layout="wide")
st.title("Evaluate the model")
st.write("Before asking whether a model is fair, understand what errors it makes and how it compares with a simple baseline.")

st.info(
    f"Verified target encoding: {GOOD_RISK_LABEL} = Good, {BAD_RISK_LABEL} = Bad. "
    "The competition baseline predicts Good for every applicant."
)

st.subheader("What will be compared")
st.markdown(
    """
    - **All-Good baseline:** predicts label 1 for every row.
    - **Logistic regression:** a relatively transparent linear classifier.
    - **Random forest:** a nonlinear comparison model.
    """
)
st.subheader("Metrics we intend to report")
st.markdown(
    """
    - Accuracy and balanced accuracy.
    - Precision, recall, and F1, with the positive class explicitly named.
    - Confusion matrix and the two types of class error.
    - UCI's documented cost matrix, kept separate from fairness metrics.
    """
)
st.warning(
    "No model has been trained in this starter repository. Results will appear here only "
    "after the evaluation pipeline has been implemented and run. No sample scores are fabricated."
)
