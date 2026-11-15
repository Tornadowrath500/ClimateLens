from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from fairlens.ui import AMBER, GREEN, callout, header, setup_page, show_chart, sidebar, style

setup_page("Health equity lab")
sidebar()

header(
    "Health equity lab",
    "A transparent, synthetic exercise for exploring how model thresholds and score shifts can change group error rates.",
)

callout(
    "Illustration only — not clinical evidence",
    "Every record and result on this page is simulated. This lab does not use patient data, evaluate a medical model, "
    "recommend care, or establish that any real system is fair or unfair. It is a discussion aid for teams adapting "
    "FairLens methods to health settings.",
    "caution",
)

st.subheader("Shape a hypothetical screening scenario")
left, right = st.columns(2)
with left:
    threshold = st.slider("Positive-screen threshold", 0.10, 0.90, 0.50, 0.01,
                          help="A record is flagged when its simulated score meets or exceeds this value.")
    score_shift = st.slider("Simulated score shift for Group B", 0.00, 0.30, 0.08, 0.01,
                            help="A deliberate score offset used to illustrate sensitivity to group-level measurement differences.")
with right:
    prevalence_b = st.slider("Simulated condition prevalence in Group B", 0.10, 0.40, 0.22, 0.01,
                             help="Changes only the invented label mix. It is not an estimate for any population.")
    st.markdown(
        "**What changes:** prevalence changes the share of simulated positive labels; score shift changes Group B's "
        "scores while keeping the label-generation rule fixed."
    )

# Fixed random seed keeps the toy data stable between reruns; sliders alter only the stated assumptions.
rng = np.random.default_rng(314159)
n = 6000
group_a_y = rng.random(n) < 0.18
group_b_y = rng.random(n) < prevalence_b
score_a = np.clip(rng.normal(np.where(group_a_y, 0.70, 0.30), 0.18), 0, 1)
score_b = np.clip(rng.normal(np.where(group_b_y, 0.70, 0.30) - score_shift, 0.18), 0, 1)

def rates(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    predicted = scores >= threshold
    positive = labels
    negative = ~labels
    return {
        "screen_rate": float(predicted.mean()),
        "sensitivity": float(predicted[positive].mean()) if positive.any() else float("nan"),
        "specificity": float((~predicted[negative]).mean()) if negative.any() else float("nan"),
        "miss_rate": float((~predicted[positive]).mean()) if positive.any() else float("nan"),
        "n": int(labels.size),
    }

a = rates(group_a_y, score_a)
b = rates(group_b_y, score_b)
st.subheader("Simulated outcomes at this threshold")
cols = st.columns(2)
for col, name, result in ((cols[0], "Group A", a), (cols[1], "Group B", b)):
    with col:
        st.markdown(f"#### {name} · {result['n']:,} invented records")
        st.metric("Screen-positive rate", f"{result['screen_rate']:.1%}")
        st.metric("Sensitivity (positive-label detection)", f"{result['sensitivity']:.1%}")
        st.metric("Specificity (negative-label non-flag rate)", f"{result['specificity']:.1%}")
        st.metric("Miss rate among positive labels", f"{result['miss_rate']:.1%}")

gap = abs(a["sensitivity"] - b["sensitivity"])
st.metric("Absolute sensitivity gap in this simulation", f"{gap:.1%}")
if gap >= 0.10:
    st.warning("This chosen synthetic setup produces a notable sensitivity difference. It is an invitation to inspect assumptions, not a verdict about a real system.")
else:
    st.info("This chosen synthetic setup produces a smaller sensitivity difference. Similar rates here do not prove real-world fairness.")

st.subheader("What happens across every threshold?")
grid = np.linspace(0.05, 0.95, 91)
sens_a = [float((score_a[group_a_y] >= t).mean()) for t in grid]
sens_b = [float((score_b[group_b_y] >= t).mean()) for t in grid]
fig = go.Figure()
fig.add_trace(go.Scatter(x=grid, y=sens_a, name="Group A", line=dict(color=GREEN, width=2.5)))
fig.add_trace(go.Scatter(x=grid, y=sens_b, name="Group B", line=dict(color=AMBER, width=2.5, dash="dash")))
fig.add_vline(x=threshold, line=dict(color="#9aacc2", dash="dot"), annotation_text="your threshold")
fig.update_xaxes(title="Screen threshold")
fig.update_yaxes(title="Sensitivity (share of positive labels flagged)", tickformat=".0%", range=[0, 1])
show_chart(style(fig, 340))
st.caption("Simulated curves. The vertical gap between lines is the sensitivity gap at each threshold; raising the shift widens it. It shows how a measurement difference can matter, not that it does in any real system.")

st.subheader("Watch the gap move")
st.caption("Press play, or drag the slider. Same simulated screen, threshold swept from 0.10 to 0.90.")
_ts = [round(float(t), 2) for t in np.arange(0.10, 0.91, 0.05)]
_names = ["Group A", "Group B"]


def _sens_pair(t):
    return [float((score_a[group_a_y] >= t).mean()), float((score_b[group_b_y] >= t).mean())]


def _bar(t):
    v = _sens_pair(t)
    return go.Bar(x=_names, y=v, marker_color=[GREEN, AMBER], text=[f"{x:.0%}" for x in v], textposition="outside")


anim = go.Figure(
    data=[_bar(_ts[0])],
    frames=[go.Frame(name=f"{t:.2f}", data=[_bar(t)], layout=go.Layout(title_text=f"Threshold {t:.2f}: sensitivity gap {abs(_sens_pair(t)[0] - _sens_pair(t)[1]):.0%}")) for t in _ts],
)
anim.update_layout(
    title_text=f"Threshold {_ts[0]:.2f}: sensitivity gap {abs(_sens_pair(_ts[0])[0] - _sens_pair(_ts[0])[1]):.0%}",
    updatemenus=[dict(type="buttons", showactive=False, x=0, y=-0.2, buttons=[
        dict(label="▶ Play sweep", method="animate", args=[None, {"frame": {"duration": 500, "redraw": True}, "transition": {"duration": 300}, "fromcurrent": True}]),
        dict(label="⏸ Pause", method="animate", args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}]),
    ])],
    sliders=[dict(active=0, x=0.22, len=0.78, y=-0.12, currentvalue={"prefix": "Threshold: "}, steps=[
        dict(label=f"{t:.2f}", method="animate", args=[[f"{t:.2f}"], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}, "transition": {"duration": 0}}]) for t in _ts])],
)
anim.update_yaxes(range=[0, 1.1], tickformat=".0%", title="Sensitivity (simulated)")
show_chart(style(anim, 440))
st.caption("Simulated data only. A widening gap shows how a threshold can interact with a measurement difference; it is not a finding about any real screening tool.")

st.subheader("Same audit, different stakes")
st.caption("FairLens audits a credit benchmark. The questions carry over to screening; the evidence does not. This table is a translation of method, not a result.")
st.markdown(
    "| Credit audit (this app) | Screening analogue (simulated here) | Why it matters |\n"
    "| --- | --- | --- |\n"
    "| Bad case classified Good (cost 5) | Missed positive case (miss rate) | The costlier error should be named before comparing groups. |\n"
    "| Good case classified Bad (cost 1) | Unnecessary flag | Over-flagging has real burdens too, so report both. |\n"
    "| Decision threshold | Screening threshold | One cut-off can affect groups unequally. |\n"
    "| Age as a sensitive input and proxy test | Group attributes and their proxies | Dropping a column rarely removes the information. |\n"
    "| Label from a 1994 benchmark | Outcome label from records | A label can reflect access or workflow, not only underlying status. |"
)

st.subheader("How to use this in a health-sector review")
st.markdown(
    "1. **Start with intended use.** Define the decision, population, setting, and who is affected before choosing metrics.\n"
    "2. **Check label meaning.** A recorded outcome may reflect access, follow-up, or workflow—not only underlying health.\n"
    "3. **Inspect measurement and missingness.** Compare how inputs are collected across groups and sites.\n"
    "4. **Review uncertainty and harms.** Report group counts and uncertainty; discuss both missed cases and unnecessary flags with clinical and community experts.\n"
    "5. **Validate locally before use.** This toy exercise cannot replace clinical validation, privacy review, or monitoring."
)
st.caption("This lab is deterministic for reproducibility. Changing its sliders changes assumptions, not external data. No information is synced from live patient or population sources.")

