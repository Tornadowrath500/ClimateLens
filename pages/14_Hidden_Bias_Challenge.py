from __future__ import annotations

import pandas as pd
import streamlit as st

from fairlens.metrics import group_outcome_metrics
from fairlens.ui import get_audit, get_op, header, require_data, setup_page, sidebar, show_table

setup_page("Hidden bias challenge")
settings = sidebar()
header(
    "Find the hidden bias",
    "Make a prediction about group outcomes, then reveal what this model did on its validation sample.",
)
data = require_data()
audit = get_audit(data, settings)
op = get_op()

y = audit.y("validation")
groups = audit.groups("validation")
predictions = op.apply(audit.proba(settings.model, "validation"), groups)
metrics = group_outcome_metrics(y, predictions, groups).sort_values("group").reset_index(drop=True)

st.caption(f"{settings.model} · validation split · {op.describe()}")
st.markdown("### Before the reveal")
st.write(
    "The model labels a record **Good** or **Bad**. Based on the selected model and decision rule, "
    "which pattern do you expect in the share labelled Good for the two age groups?"
)
guess = st.radio(
    "Your prediction",
    ["About the same (within 5 percentage points)", "Under 25 is higher", "25 or older is higher"],
    key="bias_challenge_guess",
)

if st.button("Reveal the measured outcomes", type="primary"):
    st.session_state["bias_challenge_revealed"] = True

if st.session_state.get("bias_challenge_revealed"):
    st.markdown("### What the validation sample shows")
    display = metrics[["group", "sample_count", "predicted_good_rate", "predicted_good_ci_low", "predicted_good_ci_high"]].copy()
    display = display.rename(columns={
        "group": "Age group", "sample_count": "Applicants (n)",
        "predicted_good_rate": "Classified Good", "predicted_good_ci_low": "95% interval (low)",
        "predicted_good_ci_high": "95% interval (high)",
    })
    for col in ("Classified Good", "95% interval (low)", "95% interval (high)"):
        display[col] = display[col].map(lambda value: f"{value:.1%}" if pd.notna(value) else "n/a")
    show_table(display)

    by_group = metrics.set_index("group")
    young, old = "Under 25", "25 or older"
    if young in by_group.index and old in by_group.index:
        difference = float(by_group.loc[young, "predicted_good_rate"] - by_group.loc[old, "predicted_good_rate"])
        if abs(difference) <= 0.05:
            measured = "About the same (within 5 percentage points)"
        elif difference > 0:
            measured = "Under 25 is higher"
        else:
            measured = "25 or older is higher"
        st.metric("Difference in share classified Good", f"{difference:+.1%}", help="Under 25 minus 25 or older.")
        if guess == measured:
            st.success(f"Your prediction matched this sample: {measured.lower()}.")
        else:
            st.info(f"This sample showed: {measured.lower()}.")
        st.caption("The 5-point band is a game rule, not a fairness standard. Check the group counts and intervals before interpreting the gap.")
    else:
        st.warning("Both age groups are needed to score this challenge; check the group outcome table for the groups present.")

    st.warning(
        "A difference in predicted outcomes is a signal to investigate, not proof of bias, its cause, "
        "or what would happen in real lending. This is a small historical benchmark, not a lending system."
    )

if st.button("Try another prediction"):
    st.session_state["bias_challenge_revealed"] = False
    st.rerun()

