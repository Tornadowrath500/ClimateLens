from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fairlens.applicant import best_single_changes, explain, greedy_path, score, sensitive_flip_test
from fairlens.config import FEATURE_DICTIONARY, TARGET_COLUMN, feature_label, value_label
from fairlens.ui import (
    AMBER, GREEN, callout, contribution_chart, decision_chip, get_audit, get_op, header, require_data, score_bar,
    setup_page, show_chart, show_table, sidebar, style,
)

setup_page("Applicant simulator")
settings = sidebar()
header(
    "Applicant simulator",
    "Build a fictional applicant, watch the model's score move as you change things, and probe the model with "
    "what-if and twin tests. Nothing here is advice to a real person.",
)
data = require_data()
audit = get_audit(data, settings)
op = get_op()
pipe = audit.pipelines[settings.model]
X = data.drop(columns=[TARGET_COLUMN])
train = audit.splits.X_train

def typical() -> dict:
    return {c: (float(train[c].median()) if pd.api.types.is_numeric_dtype(train[c]) else train[c].mode().iloc[0]) for c in train.columns}


# ---- starting point ----------------------------------------------------------------------------------------
if "sim_seed_row" in st.session_state:  # arriving from the Applicant Map
    st.session_state["sim_base"] = st.session_state.pop("sim_seed_row").iloc[0].to_dict()
    for c in X.columns:
        st.session_state.pop(f"sim_{c}", None)
    st.session_state["sim_base_label"] = "the applicant you picked on the map"
if "sim_base" not in st.session_state:
    st.session_state["sim_base"] = typical()
    st.session_state["sim_base_label"] = "a typical applicant"

b1, b2, b3 = st.columns([1, 1, 2])
if b1.button("Random applicant"):
    st.session_state["sim_base"] = train.sample(1).iloc[0].to_dict()
    st.session_state["sim_base_label"] = "a randomly drawn applicant"
    for c in X.columns:
        st.session_state.pop(f"sim_{c}", None)
if b2.button("Reset to typical"):
    st.session_state["sim_base"] = typical()
    st.session_state["sim_base_label"] = "a typical applicant"
    for c in X.columns:
        st.session_state.pop(f"sim_{c}", None)
b3.caption(f"Starting from {st.session_state['sim_base_label']}.")
base = st.session_state["sim_base"]

# ---- profile form ------------------------------------------------------------------------------------------
vals = {}
numeric = {c for c in X.columns if pd.api.types.is_numeric_dtype(X[c])}
with st.expander("Applicant profile", expanded=True):
    cols = st.columns(3)
    for k, c in enumerate(X.columns):
        host = cols[k % 3]
        label = feature_label(c)
        if c in numeric:
            lo, hi = int(X[c].min()), int(X[c].max())
            vals[c] = host.slider(label, lo, hi, int(min(max(base[c], lo), hi)), key=f"sim_{c}", help=FEATURE_DICTIONARY[c][2])
        else:
            levels = sorted(X[c].unique())
            default = levels.index(base[c]) if base[c] in levels else 0
            vals[c] = host.selectbox(label, levels, index=default, format_func=lambda v, c=c: value_label(c, v), key=f"sim_{c}",
                                     help=FEATURE_DICTIONARY[c][2])
row = pd.DataFrame([vals])[X.columns].astype(X.dtypes.to_dict())

# ---- live result -------------------------------------------------------------------------------------------
p = score(pipe, row)
thr = op.threshold
st.markdown(decision_chip(p, thr) + f" <span style='color:#9aacc2'>using {settings.model.lower()}, {op.describe()}</span>", unsafe_allow_html=True)
score_bar(p, thr)
tab_why, tab_what, tab_twin = st.tabs(["Why this score", "What would change it", "Twin test (sensitive inputs)"])

with tab_why:
    show_chart(contribution_chart(explain(pipe, row, train), top=10, height=380))
    st.caption("Measured: how far each input moves the score compared with swapping it for values from other applicants. "
               "It describes this model, not the real world.")

with tab_what:
    changes = best_single_changes(pipe, row, train, thr)
    steps, p_end, flipped = greedy_path(pipe, row, train, thr)
    if changes.empty:
        st.write("Nothing to test.")
    else:
        st.markdown("**Best single change per input** (only inputs a request could plausibly vary)")
        show_table(changes.assign(change=lambda d: (d["p_after"] - d["p_before"]).round(3))[["feature", "from", "to", "change", "flips"]]
                   .rename(columns={"flips": "flips the decision"}))
        if not steps.empty:
            st.markdown(f"**Shortest chain found:** {len(steps)} change(s) take the score from {p:.2f} to {p_end:.2f}"
                        f"{' and flip the classification' if flipped else ' without flipping it'}.")
            show_table(steps.assign(p_after=steps["p_after"].round(3)).rename(columns={"p_after": "score after"}))
    callout("How to read this", "These are what-ifs about the <b>model</b>. Changing an input in the real world may not have the effect the model predicts, "
            "and FairLens must never be used to coach or decide about real applicants.", "caution")

with tab_twin:
    st.write("One-click counterfactual: ask whether this model's prediction would change if the same fictional applicant belonged to another group. Keep every other answer identical.")
    tw = sensitive_flip_test(pipe, row, train, thr)
    original_probability = score(pipe, row)
    age_value = float(row.iloc[0].get("Attribute13", 22))
    other_age = 40 if age_value < 25 else 22
    age_variant = f"Age {other_age}"
    labels = [f"{r.changed_input}: {r.variant}" for r in tw.itertuples()]
    default_label = next((f"{r.changed_input}: {r.variant}" for r in tw.itertuples() if r.variant == age_variant), labels[0])
    selected_variant = st.selectbox("Change one demographic attribute", labels, index=labels.index(default_label))
    result_index = labels.index(selected_variant)
    counterfactual = tw.iloc[result_index]
    left, right, delta = st.columns(3)
    left.metric("Original score · Good", f"{original_probability:.1%}", "Higher means the model leans toward Good")
    right.metric("Changed-group score · Good", f"{counterfactual['p_good']:.1%}", str(counterfactual["decision"]))
    delta.metric("Score change", f"{counterfactual['change_vs_original']:+.1%}", "Counterfactual minus original")
    if counterfactual["decision_changes"]:
        st.warning(f"The model's label changes from {'Good' if original_probability >= thr else 'Bad'} to {counterfactual['decision']} when only {selected_variant} changes.")
    else:
        st.info(f"The model's label stays {'Good' if original_probability >= thr else 'Bad'} for this counterfactual.")
    st.caption("This changes one recorded input while holding the others fixed. It does not show a real person's outcome or establish why a group difference exists. Age and other inputs may also act as proxies.")
    fig = go.Figure(go.Bar(x=tw["change_vs_original"], y=tw["changed_input"] + ": " + tw["variant"], orientation="h",
                           marker_color=[GREEN if v >= 0 else AMBER for v in tw["change_vs_original"]]))
    fig.update_xaxes(title="Change in score versus the profile above")
    show_chart(style(fig, 300))
    flips = tw[tw["decision_changes"]]
    if settings.excluded:
        st.info("Age or personal status is switched off in the sidebar, so those bars are zero by design. That does not prove the model ignores "
                "them: other inputs can act as proxies. See the Proxy detector.")
    st.write(f"{len(flips)} of {len(tw)} variants flip the classification." if len(flips) else "No variant flips the classification for this profile.")
    with st.expander("Details"):
        show_table(tw.round(3))
