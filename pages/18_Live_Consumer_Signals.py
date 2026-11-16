from __future__ import annotations

from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fairlens.live_data import CFPB_SOURCE_URL, fetch_complaint_summary
from fairlens.ui import callout, header, setup_page, style


@st.cache_data(ttl=3600, show_spinner=False)
def cached_complaint_summary(start: date, end_exclusive: date) -> dict:
    return fetch_complaint_summary(start, end_exclusive)


setup_page("Live consumer signals")
header(
    "Live consumer signals",
    "A regularly refreshed view of consumer complaints reported to the U.S. Consumer Financial Protection Bureau.",
)

callout(
    "A separate signal, not a fairness score",
    "Complaint counts reflect reports that reached the CFPB and passed its publication process. They are not a representative sample of consumers, verified findings of wrongdoing, or evidence about loan approvals, model outcomes, or discrimination. Counts also lack a market-size denominator. Use this page for current context only; FairLens’s historical German Credit benchmark remains unchanged.",
    "caution",
)

today = datetime.now(ZoneInfo("America/Los_Angeles")).date()
range_days = st.selectbox(
    "Time window",
    options=(2, 30, 90, 365),
    format_func=lambda days: f"Past {days} days",
    index=0,
    help="The selected period ends today in Pacific Time. The CFPB API’s maximum date is exclusive.",
)
start_date = today - timedelta(days=range_days - 1)
end_date_exclusive = today + timedelta(days=1)

if st.button("Refresh now", icon=":material/refresh:", help="Clear the one-hour cache and request the CFPB again."):
    cached_complaint_summary.clear()
    st.rerun()

st.caption(f"Received {start_date:%b %d, %Y} through {today:%b %d, %Y} (Pacific Time) · Updates at the source are generally daily; FairLens caches results for up to one hour.")

try:
    with st.spinner("Loading aggregated complaint data from the CFPB…"):
        summary = cached_complaint_summary(start_date, end_date_exclusive)
except Exception as exc:
    st.error("The live CFPB feed could not be loaded right now.")
    st.caption("Check your connection or try Refresh now. FairLens does not substitute sample or invented counts.")
    with st.expander("Technical details"):
        st.code(str(exc))
    st.link_button("Open the CFPB complaint database", CFPB_SOURCE_URL)
    st.stop()

if summary["is_data_stale"]:
    st.warning("The CFPB marks its indexed data as stale. Treat the totals below as delayed.")
if summary["has_data_issue"]:
    st.warning("The CFPB reports a data-quality issue. Review its source before interpreting these counts.")

left, right = st.columns(2)
left.metric("Published complaints in this window", f"{summary['total']:,}")
last_updated = summary["last_updated"] or summary["last_indexed"]
right.metric("CFPB source status", "Indexed" if last_updated else "Available", help=f"CFPB metadata: {last_updated or 'no timestamp provided'}")
if last_updated:
    st.caption(f"CFPB metadata timestamp: {last_updated} (as supplied by the source).")

products = summary["products"][:10]
if products:
    st.subheader("Most common product categories")
    st.write("Counts are complaints by selected product category. They are not rates and should not be compared as if each product had the same number of customers.")
    frame = pd.DataFrame(products).sort_values("count", ascending=True)
    fig = go.Figure(go.Bar(
        x=frame["count"],
        y=frame["product"],
        orientation="h",
        marker=dict(color=frame["count"], colorscale=[[0, "#61c9ff"], [1, "#42ddb3"]]),
        hovertemplate="%{y}<br>%{x:,} complaints<extra></extra>",
    ))
    fig.update_layout(xaxis_title="Published complaints", yaxis_title="", height=max(340, 38 * len(frame)), showlegend=False)
    st.plotly_chart(style(fig, max(340, 38 * len(frame))), use_container_width=True)
else:
    st.info("The CFPB returned no product categories for this date range.")

st.subheader("How to read this feed")
st.markdown(
    "- A complaint is a consumer’s report, not a confirmed violation or a complete account of an interaction.\n"
    "- The CFPB generally publishes a complaint after the company responds or after 15 days, whichever comes first, and after it confirms a commercial relationship.\n"
    "- Counts are not normalized by company size, product volume, or customer base.\n"
    "- This U.S. source does not update or validate the app’s German historical benchmark and cannot establish model fairness."
)
st.link_button("View the CFPB database and methodology", CFPB_SOURCE_URL)
