from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from fairlens.applicant import best_single_changes, explain, greedy_path, score
from fairlens.config import SENSITIVE_COLUMNS
from fairlens.data import group_labels
from fairlens.mapview import KIND_FALSE_BAD, KIND_FALSE_GOOD, KIND_OK, build_map, look_alikes, terrain, terrain_summary
from fairlens.ui import (
    AMBER, GREEN, INK, MUTED, SAGE, callout, contribution_chart, decision_chip, friendly_profile, get_audit, get_op,
    header, require_data, score_bar, setup_page, show_chart, show_table, sidebar, style,
)

setup_page("Applicant map")
settings = sidebar()
header(
    "Applicant map",
    "Every dot is one applicant, placed near others with a similar financial profile. Colour the map, switch on the "
    "fairness terrain, and click a dot to see why the model scored that person the way it did.",
)
data = require_data()
audit = get_audit(data, settings)
op = get_op()
YOUNG, OLD = group_labels()

c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])
colour_by = c1.selectbox("Colour dots by", ["Model score", "Age group", "Mistakes", "Actual label"], key="map_colour")
terrain_on = c2.toggle("Fairness terrain overlay", value=True, key="map_terrain",
                       help="Shades regions where look-alike applicants from the two age groups are classified Good at different rates.")
more = c3.toggle("Include training applicants", value=False, key="map_train",
                 help="Denser map and more reliable terrain. The model has already seen these applicants, so score-based results look rosier.")
bins = c4.slider("Terrain grid", 3, 8, 5, key="map_bins")
min_n = st.slider("Minimum applicants per group in a region", 3, 15, 5, key="map_min",
                  help="Regions with fewer applicants in either age group are left blank instead of showing a noisy gap.")


@st.cache_data(show_spinner="Building the map...")
def _map(_audit, model: str, excluded: tuple, threshold: float, per_group: tuple, train: bool, key: str):
    from fairlens.evaluation import OperatingPoint
    return build_map(_audit, model, OperatingPoint(threshold, dict(per_group) or None), train)


md = _map(audit, settings.model, settings.excluded, op.threshold, tuple(sorted((op.per_group or {}).items())), more,
          f"{len(data)}-{st.session_state.get('use_demo_data', False)}")
frame = md.frame
t = terrain(frame, bins, min_n)
summary = terrain_summary(t)

COLORS = {
    "Age group": {YOUNG: AMBER, OLD: GREEN},
    "Mistakes": {KIND_OK: SAGE, KIND_FALSE_GOOD: "#ff766e", KIND_FALSE_BAD: AMBER},
    "Actual label": {True: GREEN, False: AMBER},
}
if colour_by == "Model score":
    marker = dict(size=9, color=frame["p_good"], colorscale=[[0, AMBER], [0.5, "#e8ece6"], [1, GREEN]], cmin=0, cmax=1,
                  # Keep this scale above the plot. Plotly otherwise places it at
                  # the same right edge as the terrain scale, which makes both
                  # titles and tick labels collide.
                  colorbar=dict(
                      title="Model score", orientation="h", x=0.34, xanchor="center",
                      y=1.14, yanchor="bottom", len=0.42, thickness=10,
                      tickformat=".1f", outlinewidth=0,
                  ), line=dict(width=0.6, color="#ffffff"))
else:
    key = {"Age group": "group", "Mistakes": "kind", "Actual label": "actual_good"}[colour_by]
    marker = dict(size=9, color=[COLORS[colour_by][v] for v in frame[key]], line=dict(width=0.6, color="#ffffff"))
marker["symbol"] = ["diamond" if g == YOUNG else "circle" for g in frame["group"]]

fig = go.Figure()
if terrain_on and summary["regions"]:
    xe, ye = np.linspace(frame["x"].min(), frame["x"].max(), bins + 1), np.linspace(frame["y"].min(), frame["y"].max(), bins + 1)
    z = np.full((bins, bins), np.nan)
    tip = np.full((bins, bins), "", dtype=object)
    for r in t[t["reliable"]].itertuples():
        z[r.cy, r.cx] = r.gap
        tip[r.cy, r.cx] = (f"Region: {r.n_young} younger / {r.n_old} older applicants<br>"
                           f"Classified Good: {r.rate_young:.0%} vs {r.rate_old:.0%}<br>Gap {r.gap:+.0%}")
    fig.add_trace(go.Heatmap(
        x=(xe[:-1] + xe[1:]) / 2, y=(ye[:-1] + ye[1:]) / 2, z=z, text=tip, hoverinfo="text", hoverongaps=False, opacity=0.55,
        colorscale=[[0, "#e0a441"], [0.5, "#f4f2ea"], [1, "#6aa58f"]], zmin=-0.4, zmax=0.4, showscale=True,
        colorbar=dict(
            title="Younger minus<br>older rate", x=1.03, xanchor="left", y=0.5,
            len=0.86, thickness=12, tickformat="+.0%", outlinewidth=0,
        ), xgap=2, ygap=2,
    ))
scatter_curve = len(fig.data)
fig.add_trace(go.Scatter(
    x=frame["x"], y=frame["y"], mode="markers", marker=marker, showlegend=False, customdata=np.arange(len(frame)),
    hovertemplate="Applicant %{customdata}<br>Score %{text}<extra></extra>", text=[f"{v:.2f}" for v in frame["p_good"]],
    unselected=dict(marker=dict(opacity=0.55)),
))
fig.update_xaxes(title=f"Similarity axis 1 ({md.explained[0]:.0%} of variation)", showticklabels=False)
fig.update_yaxes(title=f"Similarity axis 2 ({md.explained[1]:.0%})", showticklabels=False)
style(fig, 600)
has_terrain_scale = terrain_on and bool(summary["regions"])
has_score_scale = colour_by == "Model score"
fig.update_layout(
    clickmode="event+select", dragmode="select",
    # Reserve dedicated space for the horizontal score scale, the vertical
    # terrain scale, and the long similarity-axis titles.
    margin=dict(
        l=72, r=175 if has_terrain_scale else 32,
        t=100 if has_score_scale else 48, b=72,
    ),
)
try:
    event = st.plotly_chart(fig, theme=None, width="stretch", config={"responsive": True, "displaylogo": False},
                            on_select="rerun", selection_mode="points", key="applicant_map")
except TypeError:
    event = st.plotly_chart(fig, theme=None, use_container_width=True, config={"responsive": True, "displaylogo": False},
                            on_select="rerun", selection_mode="points", key="applicant_map")

legend = {"Model score": "Colour = model's score for Good (amber low, green high)",
          "Age group": f"Amber = {YOUNG}, green = {OLD}", "Mistakes": "Red = costly mistake, amber = turned away wrongly, sage = correct",
          "Actual label": "Green = labelled Good, amber = labelled Bad"}[colour_by]
st.caption(f"{legend}. Diamonds are {YOUNG}; circles are {OLD}. Positions come from non-sensitive inputs only. "
           f"{len(frame)} applicants ({'validation + training' if more else 'validation only'}).")

# ---- terrain readout ------------------------------------------------------------------------------------------
st.subheader("What the terrain says")
if not summary["regions"]:
    st.info("No region has enough applicants from both age groups. Lower the minimum, use a coarser grid, or include training applicants.")
else:
    w = summary["weighted_gap"]
    st.markdown(
        f"- **Measured:** across {summary['regions']} regions with enough applicants from both groups ({summary['applicants_covered']} people), "
        f"{YOUNG} look-alikes are classified Good **{abs(w) * 100:.1f} points {'less' if w < 0 else 'more'} often** than {OLD} look-alikes on average.\n"
        f"- **Largest gap:** {abs(summary['worst']['gap']) * 100:.0f} points in a region with {int(summary['worst']['n_young'])} younger and "
        f"{int(summary['worst']['n_old'])} older applicants.\n"
        f"- **Limitation:** regions are coarse and counts are small. A gap shows where to look, not why it exists."
    )
    with st.expander("Region table"):
        show_table(t[t["reliable"]].assign(gap=lambda d: d["gap"].round(3), rate_young=lambda d: d["rate_young"].round(3), rate_old=lambda d: d["rate_old"].round(3))
                   [["n_young", "n_old", "rate_young", "rate_old", "gap"]].sort_values("gap"))

# ---- selected applicant ------------------------------------------------------------------------------------
st.subheader("Inspect an applicant")
picked = None
try:
    pts = [q for q in event.selection.points if q.get("curve_number", scatter_curve) == scatter_curve]
    if pts:
        picked = int(pts[0]["point_index"])
except Exception:
    picked = None
manual = st.number_input("Or type an applicant number (shown on hover)", 0, len(frame) - 1, 0, key="map_manual")
if picked is None:
    st.caption("Click or box-select dots on the map to inspect one. Until then, showing the applicant number above.")
i = int(picked if picked is not None else manual)

row = md.X.iloc[[i]]
pipe = audit.pipelines[settings.model]
thr = op.threshold if not op.per_group else op.per_group.get(frame.loc[i, "group"], op.threshold)
p = score(pipe, row)
left, right = st.columns([1, 1.25])
with left:
    st.markdown(f"**Applicant {i}** · {frame.loc[i, 'group']} · labelled {'Good' if frame.loc[i, 'actual_good'] else 'Bad'} in the data")
    st.markdown(decision_chip(p, thr), unsafe_allow_html=True)
    score_bar(p, thr)
    show_table(friendly_profile(row))
with right:
    st.markdown("**Why this score?** (each input's push versus a typical applicant)")
    show_chart(contribution_chart(explain(pipe, row, audit.splits.X_train)))
    st.caption("Measured by swapping one input at a time for values from other applicants. Interpretation, not causation.")

la = look_alikes(md, i)
st.markdown("**Look-alike check**")
a, b = st.columns(2)
for col, key, label in ((a, "same", "same age group"), (b, "other", "other age group")):
    r = la[key]
    col.metric(f"15 closest look-alikes, {label}", f"{r['classified_good']:.0%} classified Good",
               f"{r['actual_good']:.0%} labelled Good in the data", delta_color="off")
st.caption("Look-alikes are matched on every input except age and personal status. A big difference between the two numbers "
           "is a prompt to investigate, not proof of unequal treatment.")

with st.expander("What would change this decision? (illustrative)"):
    steps, p_end, flipped = greedy_path(pipe, row, audit.splits.X_train, thr)
    if steps.empty:
        st.write("No single change among the tested inputs moves this score.")
    else:
        show_table(steps.assign(p_after=steps["p_after"].round(3)).rename(columns={"p_after": "score after"}))
        st.write(("These changes would flip the model's classification." if flipped else "Even these changes would not flip the classification.")
                 + " This describes the model, not what an applicant should do.")
if st.button("Open this applicant in the Simulator", type="primary"):
    st.session_state["sim_seed_row"] = row.reset_index(drop=True)
    st.switch_page("pages/8_Applicant_Simulator.py")

