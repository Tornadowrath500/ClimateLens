from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from fairlens.data import group_labels
from fairlens.mitigation import build_strategies, evaluate_strategies
from fairlens.ui import AMBER, GREEN, INK, callout, header, require_data, setup_page, show_chart, show_table, sidebar, style

setup_page("Mitigation lab")
settings = sidebar()
header(
    "Mitigation lab",
    "Six ways to change a model's behaviour, scored side by side on the same validation applicants. "
    "Each one moves some numbers and costs something else. None is a guaranteed fix.",
)
data = require_data()
YOUNG, OLD = group_labels()


@st.cache_data(show_spinner="Training every strategy on the same split...")
def _run(_data, model: str, key: str):
    strategies, y, g = build_strategies(_data, model)
    return strategies, evaluate_strategies(strategies, y, g)


strategies, table = _run(data, settings.model, f"{len(data)}-{st.session_state.get('use_demo_data', False)}")
metric = st.radio(
    "Which gap do you care about?",
    ["Classified Good", "False Good (Bad cases called Good)", "False Bad (Good cases called Bad)"],
    horizontal=True, key="mit_metric",
    help="Each is the younger group's rate minus the older group's rate. The right choice depends on what a mistake costs people.",
)
col = {"Classified Good": "gap_classified_good", "False Good (Bad cases called Good)": "gap_false_good",
       "False Bad (Good cases called Bad)": "gap_false_bad"}[metric]

fig = go.Figure()
for _, r in table.iterrows():
    fig.add_trace(go.Scatter(
        x=[r["cost_per_applicant"]], y=[abs(r[col])], mode="markers+text", text=[r["strategy"]], textposition="top center",
        marker=dict(size=15, color=AMBER if "what-if" in r["strategy"] else GREEN, symbol="diamond" if r["strategy"] == "Baseline" else "circle"),
        hovertemplate=f"{r['strategy']}<br>Cost per applicant %{{x:.2f}}<br>Absolute gap %{{y:.1%}}<extra></extra>", showlegend=False,
    ))
fig.update_xaxes(title="UCI cost per applicant (lower is better)")
fig.update_yaxes(title="Absolute gap between age groups (lower is closer)", tickformat=".0%", rangemode="tozero")
st.subheader("The trade-off map")
show_chart(style(fig, 440))
st.caption("Bottom-left is ideal. Notice how rarely a strategy improves both axes. Amber marks a what-if that treats groups differently.")

best_gap = table.loc[table[col].abs().idxmin()]
best_cost = table.loc[table["cost_per_applicant"].idxmin()]
st.markdown(
    f"- **Measured:** the smallest {metric.lower()} gap is **{best_gap['strategy']}** ({best_gap[col]:+.1%}); the lowest cost is **{best_cost['strategy']}** "
    f"({best_cost['cost_per_applicant']:.2f} per applicant).\n"
    "- **Limitation:** the younger group is small on validation data, so the bootstrap intervals below are wide. Differences between strategies "
    "are often smaller than the noise.\n"
    "- **Interpretation:** a strategy that closes one gap can open another. Pick it only with a reason that fits the real-world harm."
)

show = table.assign(**{
    "Gap, classified Good": table["gap_classified_good"].map("{:+.1%}".format),
    "95% interval": [f"{lo:+.1%} to {hi:+.1%}" for lo, hi in zip(table["gap_classified_good_lo"], table["gap_classified_good_hi"])],
    "Gap, false Good": table["gap_false_good"].map("{:+.1%}".format), "Gap, false Bad": table["gap_false_bad"].map("{:+.1%}".format),
    "Cost": table["cost_per_applicant"].round(3), "Accuracy": table["accuracy"].map("{:.1%}".format),
})[["strategy", "Cost", "Accuracy", "Gap, classified Good", "95% interval", "Gap, false Good", "Gap, false Bad"]]
show_table(show)
st.download_button("Download comparison (CSV)", table.to_csv(index=False), "fairlens_mitigation_comparison.csv", "text/csv")

st.subheader("What each strategy does")
for s_ in strategies.values():
    st.markdown(f"**{s_.name}** · {s_.blurb}")
    if s_.caution:
        st.warning(s_.caution)
callout("Honest framing", "Reweighing and threshold changes are standard research techniques, but a model that looks fairer on one metric in one validation "
        "split may not generalise. Treat this page as a way to build intuition about trade-offs.")
