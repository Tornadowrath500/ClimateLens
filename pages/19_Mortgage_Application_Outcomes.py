from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fairlens.hmda import (
    HMDA_ACTIONS,
    HMDA_API_DOCS_URL,
    HMDA_DATASET_URL,
    HMDA_GROUPS,
    fetch_hmda_aggregations,
)
from fairlens.ui import callout, header, setup_page, style

STATES = {
    "Nationwide": None,
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA",
    "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA",
    "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR",
    "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA",
    "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}


@st.cache_data(ttl=3600, show_spinner=False)
def cached_hmda_aggregations(year: int, group_by: str, state: str | None) -> dict:
    return fetch_hmda_aggregations(year, group_by, state)


setup_page("Mortgage application outcomes")
header(
    "Mortgage application outcomes",
    "Explore recent U.S. mortgage application outcomes by reported applicant demographics.",
)

st.markdown(
    '<div class="fl-scope"><span class="fl-chip good">PUBLIC AGGREGATES</span>'
    "HMDA reports mortgage applications and actions taken; this page does not evaluate a lender's internal model.</div>",
    unsafe_allow_html=True,
)
callout(
    "What this comparison can—and cannot—say",
    "A difference in reported outcomes can identify a pattern worth investigating. These counts do not show applicants’ full financial profiles, underwriting criteria, or why a decision was made. Public HMDA records are modified to protect privacy and cover only institutions and mortgages that must report. A gap is not, by itself, proof of discrimination or causation.",
    "caution",
)

filters = st.columns([1, 1, 1.4], vertical_alignment="bottom")
year = filters[0].selectbox("Data year", list(range(2025, 2017, -1)), index=0)
state_name = filters[1].selectbox("Geography", list(STATES), index=0)
group_by = filters[2].selectbox("Compare reported", list(HMDA_GROUPS), index=0)
state = STATES[state_name]

if st.button("Refresh data", icon=":material/refresh:", help="Clear the one-hour cache and request the HMDA aggregate report again."):
    cached_hmda_aggregations.clear()
    st.rerun()

st.caption(
    f"HMDA year {year} · {state_name} · Grouped by {group_by.lower()} · "
    "The Data Browser’s 2025 view uses the snapshot dataset, frozen June 2, 2026."
    if year == 2025
    else f"HMDA year {year} · {state_name} · Grouped by {group_by.lower()} · Counts cover action codes 1–5."
)

try:
    with st.spinner("Loading aggregate application outcomes from HMDA…"):
        report = cached_hmda_aggregations(year, group_by, state)
except Exception as exc:
    st.error("The HMDA report could not be loaded right now.")
    st.caption("Try Refresh data or use the official HMDA Data Browser. FairLens does not fill gaps with sample counts.")
    with st.expander("Technical details"):
        st.code(str(exc))
    st.link_button("Open the official HMDA Data Browser", "https://ffiec.cfpb.gov/data-browser/")
    st.stop()

frame = pd.DataFrame(report["rows"])
if frame.empty:
    st.info("HMDA returned no records for these filters.")
    st.link_button("Open the official HMDA Data Browser", "https://ffiec.cfpb.gov/data-browser/")
    st.stop()

pivot = frame.pivot_table(index="group", columns="action", values="count", aggfunc="sum", fill_value=0)
for code in HMDA_ACTIONS:
    if code not in pivot.columns:
        pivot[code] = 0
pivot = pivot[list(HMDA_ACTIONS)]
pivot["total"] = pivot.sum(axis=1)
pivot["approved_or_originated"] = pivot["1"] + pivot["2"]
pivot["denied_share"] = pivot["3"].div(pivot["total"].where(pivot["total"] > 0))
pivot = pivot.sort_values("total", ascending=False)

total_records = int(pivot["total"].sum())
total_denied = int(pivot["3"].sum())
overall_denied_share = total_denied / total_records if total_records else 0
a, b, c = st.columns(3)
a.metric("Records with actions 1–5", f"{total_records:,}")
b.metric("Records coded as denied", f"{overall_denied_share:.1%}", help=f"{total_denied:,} of {total_records:,} records. This is an unadjusted share, not an applicant-specific risk.")
c.metric("Source response", str(report["served_from"] or "HMDA API").title())

st.subheader(f"Reported outcomes by {group_by.lower()}")
st.write(
    "Each bar shows the share of records for that group assigned each final-action code. "
    "The denominator includes originated, approved-not-accepted, denied, withdrawn, and incomplete records. "
    "Purchased loans and preapproval requests are excluded."
)

fig = go.Figure()
colors = {"1": "#42ddb3", "2": "#61c9ff", "3": "#f2b84b", "4": "#b39aff", "5": "#8297ab"}
action_counts = pivot[list(HMDA_ACTIONS)]
denominators = pivot["total"]
for code, label in HMDA_ACTIONS.items():
    counts = action_counts[code]
    shares = counts.div(denominators.where(denominators > 0)).fillna(0) * 100
    fig.add_trace(
        go.Bar(
            x=shares,
            y=pivot.index,
            orientation="h",
            name=label,
            marker_color=colors[code],
            customdata=counts,
            hovertemplate="%{y}<br>" + label + ": %{customdata:,} (%{x:.1f}%)<extra></extra>",
        )
    )
fig.update_layout(
    barmode="stack",
    xaxis_title="Share of reported records (%)",
    yaxis_title="",
    xaxis=dict(range=[0, 100], ticksuffix="%"),
    height=max(380, 48 * len(pivot)),
    legend=dict(orientation="h", y=-0.28, x=0),
)
st.plotly_chart(style(fig, max(380, 48 * len(pivot))), use_container_width=True)

table = pivot.rename(columns=HMDA_ACTIONS).reset_index().rename(columns={"group": group_by})
table = table.rename(columns={
    "total": "Records (actions 1–5)",
    "approved_or_originated": "Originated or approved",
    "denied_share": "Denied share (unadjusted)",
})
table["Denied share (unadjusted)"] = table["Denied share (unadjusted)"].map(lambda value: f"{value:.1%}" if pd.notna(value) else "n/a")
st.subheader("Counts behind the chart")
st.dataframe(table, hide_index=True, use_container_width=True)

if year == 2025:
    st.caption("The 2025 Data Browser results use the snapshot frozen June 2, 2026. They are the latest available reporting year, not continuously updated applicant decisions.")
else:
    st.caption("Older years are historical snapshots. The HMDA Data Browser documents which dataset version each year query uses.")

st.markdown(
    f"Sources: [HMDA Data Browser]({HMDA_API_DOCS_URL}) · "
    f"[2025 snapshot dataset]({HMDA_DATASET_URL}) · "
    "[CFPB overview of HMDA](https://www.consumerfinance.gov/data-research/hmda/)"
)
