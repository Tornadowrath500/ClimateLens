from __future__ import annotations

import io

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fairlens.byom import FOUR_FIFTHS, SMALL_GROUP, group_table, plain_summary, to_favorable
from fairlens.ui import AMBER, GREEN, SAGE, callout, get_audit, header, require_data, setup_page, show_chart, show_table, sidebar, style

setup_page("Audit your own model")
settings = sidebar()
header(
    "Audit your own model",
    "Upload a CSV of any model's decisions with a group column, and FairLens produces a transparent group comparison: "
    "rates with denominators and intervals, error rates when you have true labels, and plain-language findings.",
)
callout("Your data stays in this session", "The file is read in memory and is never written to disk or sent anywhere by FairLens. "
        "Use only data you are allowed to analyse.")

with st.expander("No file handy? Use FairLens's own validation predictions as a sample"):
    if st.button("Load sample"):
        data = require_data()
        audit = get_audit(data, settings)
        sample = pd.DataFrame({
            "approved": (audit.proba(settings.model, "validation") >= 0.5).astype(int),
            "score": audit.proba(settings.model, "validation").round(4),
            "actually_good": (audit.y("validation") == 1).astype(int),
            "age_group": audit.groups("validation"),
        })
        st.session_state["byo_csv"] = sample.to_csv(index=False)
        st.session_state["byo_name"] = "FairLens validation sample"
        st.session_state.update(byo_dec="approved", byo_grp="age_group", byo_truth="actually_good", byo_fav="1", byo_tpos="1")

up = st.file_uploader("CSV file", type=["csv"])
if up is not None:
    st.session_state["byo_csv"], st.session_state["byo_name"] = up.getvalue().decode("utf-8", errors="replace"), up.name
if "byo_csv" not in st.session_state:
    st.info("Upload a CSV to begin. Typical columns: a model decision or score, a group such as age band or region, and (optionally) the true outcome.")
    st.stop()

df = pd.read_csv(io.StringIO(st.session_state["byo_csv"]))
st.caption(f"{st.session_state['byo_name']}: {len(df):,} rows, {df.shape[1]} columns.")
if len(df) < 2:
    st.error("The file needs at least two rows.")
    st.stop()

cols = list(df.columns)
c1, c2, c3 = st.columns(3)
dec = c1.selectbox("Decision or score column", cols, key="byo_dec")
grp = c2.selectbox("Group column", [c for c in cols if c != dec], key="byo_grp")
truth_opts = ["(none)"] + [c for c in cols if c not in (dec, grp)]
truth = c3.selectbox("True outcome column (optional)", truth_opts, key="byo_truth")

numeric_score = pd.api.types.is_numeric_dtype(df[dec]) and df[dec].nunique() > 2
if numeric_score:
    thr = st.slider("Score threshold: favorable when score is at least", float(df[dec].min()), float(df[dec].max()), float(df[dec].median()), key="byo_thr")
    fav = to_favorable(df[dec], None, thr)
else:
    values = sorted(df[dec].dropna().astype(str).unique())
    fv = st.selectbox("Which value means the favorable outcome (for example, approved)?", values, index=len(values) - 1, key="byo_fav")
    fav = to_favorable(df[dec], fv)
actual = None
if truth != "(none)":
    tv = sorted(df[truth].dropna().astype(str).unique())
    tpos = st.selectbox("Which true-outcome value is the positive one?", tv, index=len(tv) - 1, key="byo_tpos")
    actual = (df[truth].astype(str) == tpos).to_numpy()

levels = sorted(df[grp].dropna().astype(str).unique())
if len(levels) < 2 or len(levels) > 20:
    st.error(f"The group column has {len(levels)} distinct values; choose a column with between 2 and 20.")
    st.stop()
ref = st.selectbox("Reference group (others are compared to it)", ["(largest group)"] + levels, key="byo_ref")
t = group_table(fav, df[grp], actual, None if ref.startswith("(") else ref)

st.subheader("Findings")
for line in plain_summary(t):
    st.markdown(f"- {line}")
fig = go.Figure()
for _, r in t.iterrows():
    fig.add_trace(go.Scatter(x=[r["selection_rate"]], y=[f"{r['group']} (n={r['n']})"], mode="markers", showlegend=False,
                             marker=dict(size=13, color=SAGE if r["small_group"] else (GREEN if r["group"] == r["reference"] else AMBER)),
                             error_x=dict(type="data", symmetric=False, array=[r["ci_high"] - r["selection_rate"]], arrayminus=[r["selection_rate"] - r["ci_low"]]),
                             hovertemplate=f"{r['group']}<br>{int(r['favorable'])} of {int(r['n'])}<extra></extra>"))
fig.update_xaxes(range=[0, 1], tickformat=".0%", title="Share receiving the favorable outcome (95% interval)")
show_chart(style(fig, 120 + 60 * len(t)))
st.caption(f"Green = reference, amber = compared group, grey = under {SMALL_GROUP} rows (very uncertain). The {FOUR_FIFTHS:.0%} line is a screening heuristic, not a legal conclusion.")
show_table(t.round(3))
st.download_button("Download group table (CSV)", t.to_csv(index=False), "fairlens_group_audit.csv", "text/csv")
if actual is None:
    st.info("Add a true-outcome column to also see true-positive and false-positive rates by group.")

