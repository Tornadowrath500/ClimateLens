"""Streamlit helpers: theme, charts, shared state. Core logic never imports this module."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from fairlens.config import (
    AGE_COLUMN,
    AGE_GROUP_CUTOFF,
    PERSONAL_STATUS_COLUMN,
    RANDOM_STATE,
    UCI_URL,
    dataset_path,
)
from fairlens.data import (
    benchmark_shape_warnings,
    dataset_provenance,
    download_dataset,
    group_labels,
    load_dataset,
)
from fairlens.evaluation import Audit, OperatingPoint, run_audit
from fairlens.models import MODEL_NAMES

INK, GREEN, SAGE, AMBER, MUTED, LINE = "#1f2d28", "#2f5d50", "#9db5a8", "#b7791f", "#5d6b65", "#e2e0d6"
YOUNG, OLD = group_labels(AGE_GROUP_CUTOFF)
GROUP_COLOR = {YOUNG: AMBER, OLD: GREEN}

METRIC_HELP = {
    "accuracy": "Share of all applicants the model labelled correctly. Misleading when errors cost different amounts.",
    "recall_good": "Of applicants whose label is Good, the share the model also called Good. High means few good-risk people are turned away.",
    "recall_bad": "Of applicants whose label is Bad, the share the model correctly called Bad. This is how many risky cases it catches.",
    "precision_good": "Of applicants the model called Good, the share who really are labelled Good. Low means many 'Good' calls are mistakes.",
    "f1": "A single balance of precision and recall for the Good class. It ignores the 5-to-1 cost, so read it alongside cost.",
    "cost": "Average UCI cost per applicant: 5 for each Bad case called Good, 1 for each Good case called Bad. Lower is better.",
    "auc": "How well the model ranks Good above Bad cases regardless of threshold. 0.5 is a coin flip, 1.0 is perfect ranking.",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=Public+Sans:wght@400;500;600&display=swap');
html, body, .stApp, [data-testid="stMarkdownContainer"] {{ font-family: 'Public Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; }}
h1, h2, h3, h4 {{ font-family: 'Newsreader', Georgia, 'Times New Roman', serif !important; color: {INK}; letter-spacing: -0.01em; font-weight: 600; }}
h1 {{ font-size: 2.5rem !important; line-height: 1.12; }}
.block-container {{ max-width: 1080px; padding-top: 2.6rem; padding-bottom: 4rem; }}
.fl-lede {{ color: {MUTED}; font-size: 1.12rem; line-height: 1.65; max-width: 46rem; margin: .2rem 0 1.4rem; }}
.fl-callout {{ border: 1px solid {LINE}; border-left: 4px solid {GREEN}; background: rgba(255,255,255,.7);
  border-radius: 8px; padding: .9rem 1.1rem; margin: .6rem 0 1.1rem; color: {INK}; line-height: 1.55; }}
.fl-callout.caution {{ border-left-color: {AMBER}; }}
.fl-callout strong {{ display: block; margin-bottom: .15rem; }}
.fl-step {{ display: flex; gap: 1rem; padding: .85rem 0; border-top: 1px solid {LINE}; }}
.fl-step:last-child {{ border-bottom: 1px solid {LINE}; }}
.fl-step b {{ font-family: 'Newsreader', Georgia, serif; font-size: 1.5rem; color: {GREEN}; min-width: 1.6rem; }}
.fl-step span {{ color: {MUTED}; }}
.fl-group {{ border: 1px solid {LINE}; border-radius: 8px; padding: .9rem 1.1rem; background: rgba(255,255,255,.7); }}
.fl-group .n {{ font-family: 'Newsreader', Georgia, serif; font-size: 2rem; color: {INK}; line-height: 1.1; }}
[data-testid="stMetric"] {{ background: rgba(255,255,255,.7); border: 1px solid {LINE}; border-radius: 8px; padding: .7rem .9rem; }}
@media (prefers-reduced-motion: reduce) {{ * {{ animation: none !important; transition: none !important; }} }}
</style>
"""


def setup_page(title: str) -> None:
    """Must be the first Streamlit call on every page."""
    st.set_page_config(page_title=f"{title} | FairLens", page_icon="◈", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)


def header(title: str, lede: str) -> None:
    st.title(title)
    st.markdown(f'<p class="fl-lede">{lede}</p>', unsafe_allow_html=True)


def callout(title: str, body: str, kind: str = "note") -> None:
    st.markdown(
        f'<div class="fl-callout {kind}"><strong>{title}</strong>{body}</div>', unsafe_allow_html=True
    )


def show_chart(fig: go.Figure) -> None:
    try:
        st.plotly_chart(fig, theme=None, width="stretch")
    except TypeError:  # older Streamlit
        st.plotly_chart(fig, theme=None, use_container_width=True)


def show_table(frame: pd.DataFrame, **kwargs) -> None:
    try:
        st.dataframe(frame, hide_index=True, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(frame, hide_index=True, use_container_width=True, **kwargs)


def style(fig: go.Figure, height: int = 340) -> go.Figure:
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Public Sans, system-ui, sans-serif", color=INK, size=13),
        legend=dict(orientation="h", y=-0.2),
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False)
    fig.update_yaxes(gridcolor=LINE, zeroline=False)
    return fig


# ---- shared state ---------------------------------------------------------------
@dataclass(frozen=True)
class Settings:
    model: str
    excluded: tuple[str, ...]


def sidebar() -> Settings:
    """Same widgets, same keys on every page, so choices persist while navigating."""
    with st.sidebar:
        st.markdown("### Model settings")
        model = st.radio(
            "Model", MODEL_NAMES, key="model_name",
            help="Compare models on the validation set (page 2). The test set is for a final look only.",
        )
        st.caption("Inputs the model may use")
        use_age = st.checkbox("Age", value=True, key="use_age")
        use_status = st.checkbox("Personal status and sex", value=True, key="use_status")
        st.caption(
            "Unticking an input removes it from the model. Related features can still "
            "carry the same information, so check whether the group gap actually moves."
        )
    excluded = tuple(c for c, keep in ((AGE_COLUMN, use_age), (PERSONAL_STATUS_COLUMN, use_status)) if not keep)
    return Settings(model=model, excluded=excluded)


def get_op() -> OperatingPoint:
    return st.session_state.get("op", OperatingPoint())


def set_op(op: OperatingPoint) -> None:
    st.session_state["op"] = op


@st.cache_data(show_spinner=False)
def _load(path: str, mtime: float) -> pd.DataFrame:
    return load_dataset(path)


def require_data() -> pd.DataFrame:
    """Return the validated dataset, or explain how to get it and stop the page."""
    path = dataset_path()
    if not path.exists():
        callout(
            "The dataset is not on this computer yet",
            "FairLens never downloads data on its own. Select the button to fetch the UCI German Credit "
            "file once; it is saved to <code>data/raw/</code> and kept out of Git.",
            "caution",
        )
        if st.button("Download the dataset from UCI", type="primary"):
            try:
                with st.spinner("Contacting the UCI repository..."):
                    download_dataset(output_path=path)
                _load.clear()
                st.rerun()
            except Exception as exc:  # network, package or schema problems
                st.error(f"The download failed: {exc}")
                st.markdown(
                    f"Run `python scripts/download_dataset.py` in a terminal with internet access, "
                    f"or [download it manually]({UCI_URL})."
                )
        st.stop()
    try:
        return _load(str(path), path.stat().st_mtime)
    except Exception as exc:
        st.error(f"The dataset at {path} could not be validated: {exc}")
        st.stop()


@st.cache_resource(show_spinner="Training the models on the training split...")
def _audit(_data: pd.DataFrame, excluded: tuple[str, ...], seed: int, key: float) -> Audit:
    return run_audit(_data, excluded=excluded, seed=seed)


def get_audit(data: pd.DataFrame, settings: Settings) -> Audit:
    return _audit(data, settings.excluded, RANDOM_STATE, dataset_path().stat().st_mtime)


def provenance_note(data: pd.DataFrame) -> None:
    manifest = dataset_provenance()
    problems = benchmark_shape_warnings(data)
    if not manifest:
        problems.append("No download manifest found, so the file's origin is unverified.")
    if problems:
        st.warning(" ".join(problems))
    else:
        st.caption(f"Data: UCI Statlog (German Credit), retrieved {manifest.get('retrieved_utc', '')[:10]}. CC BY 4.0.")


# ---- charts ---------------------------------------------------------------------
def pct_text(x: float) -> str:
    return "n/a" if x is None or pd.isna(x) else f"{100 * x:.0f}%"


def group_rate_chart(metrics: pd.DataFrame, height: int = 300) -> go.Figure:
    """Three dot-and-interval panels. Each axis label carries that panel's denominator."""
    panels = [
        ("predicted_good", "Classified Good", "sample_count", "predicted_good_count"),
        ("false_good", "Bad cases classified Good", "actual_bad_count", "false_good_count"),
        ("false_bad", "Good cases classified Bad", "actual_good_count", "false_bad_count"),
    ]
    fig = make_subplots(rows=1, cols=3, subplot_titles=[p[1] for p in panels], horizontal_spacing=0.17)
    table = metrics.set_index("group")
    order = [g for g in (OLD, YOUNG) if g in table.index]
    for col, (key, _, den_col, num_col) in enumerate(panels, start=1):
        rate_col = {"predicted_good": "predicted_good_rate", "false_good": "false_good_rate_among_bad",
                    "false_bad": "false_bad_rate_among_good"}[key]
        for g in order:
            r = table.loc[g]
            rate, lo, hi = r[rate_col], r[f"{key}_ci_low"], r[f"{key}_ci_high"]
            if pd.isna(rate):
                continue
            fig.add_trace(
                go.Scatter(
                    x=[rate], y=[f"{g} (n={int(r[den_col])})"], mode="markers+text",
                    marker=dict(size=13, color=GROUP_COLOR.get(g, SAGE), symbol="diamond" if g == YOUNG else "circle"),
                    error_x=dict(type="data", symmetric=False, array=[hi - rate], arrayminus=[rate - lo],
                                 color=GROUP_COLOR.get(g, SAGE), thickness=2),
                    text=[pct_text(rate)], textposition="top center", showlegend=False,
                    hovertemplate=f"{g}<br>{int(r[num_col])} of {int(r[den_col])} = {pct_text(rate)}"
                                  f"<br>95% interval {pct_text(lo)} to {pct_text(hi)}<extra></extra>",
                ),
                row=1, col=col,
            )
        fig.update_xaxes(range=[0, 1], tickformat=".0%", row=1, col=col)
    fig.update_yaxes(autorange="reversed")
    return style(fig, height)


def confusion_chart(matrix: list[list[int]]) -> go.Figure:
    labels = [["Good called Good", "Good called Bad<br>(cost 1 each)"], ["Bad called Good<br>(cost 5 each)", "Bad called Bad"]]
    text = [[f"<b>{matrix[i][j]}</b><br>{labels[i][j]}" for j in range(2)] for i in range(2)]
    fig = go.Figure(
        go.Heatmap(
            z=matrix, x=["Model says Good", "Model says Bad"], y=["Label is Good", "Label is Bad"],
            text=text, texttemplate="%{text}", colorscale=[[0, "#eef2ee"], [1, SAGE]], showscale=False,
            hoverinfo="skip", xgap=3, ygap=3,
        )
    )
    fig.update_yaxes(autorange="reversed")
    return style(fig, 300)


def cost_chart(table: pd.DataFrame) -> go.Figure:
    colors = [AMBER if "All-Bad" in m else (SAGE if "All-Good" in m else GREEN) for m in table["model"]]
    fig = go.Figure(
        go.Bar(
            x=table["cost_per_applicant"], y=table["model"], orientation="h", marker_color=colors,
            text=[f"{v:.2f}" for v in table["cost_per_applicant"]], textposition="outside",
        )
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(title="Average cost per applicant (lower is better)", rangemode="tozero")
    return style(fig, 260)


def sweep_chart(sweep: pd.DataFrame, marks: dict[str, float]) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
        subplot_titles=("Average cost per applicant (all applicants)", "Share classified Good, by age group"),
    )
    allrows = sweep[sweep["group"] == "All"]
    fig.add_trace(go.Scatter(x=allrows["threshold"], y=allrows["cost_per_applicant"], mode="lines",
                             line=dict(color=INK, width=2.5), name="Cost", showlegend=False), row=1, col=1)
    for g in (OLD, YOUNG):
        part = sweep[sweep["group"] == g]
        fig.add_trace(go.Scatter(x=part["threshold"], y=part["predicted_good_rate"], mode="lines",
                                 line=dict(color=GROUP_COLOR[g], width=2.5, dash="dash" if g == YOUNG else "solid"), name=g),
                      row=2, col=1)
    styles = {"Your setting": (GREEN, "solid"), "Best on validation": (AMBER, "dot"), "Theory (5/6)": (MUTED, "dot")}
    for label, x in marks.items():
        color, dash = styles.get(label, (MUTED, "dot"))
        for r in (1, 2):
            fig.add_vline(x=x, line=dict(color=color, dash=dash, width=1.5), row=r, col=1)
        fig.add_annotation(x=x, y=1.0, yref="paper", text=label, showarrow=False, font=dict(color=color, size=11), yanchor="bottom")
    fig.update_xaxes(title="Decision threshold: classify Good when P(Good) is at least this", row=2, col=1)
    fig.update_yaxes(tickformat=".0%", row=2, col=1)
    return style(fig, 520)


def stability_chart(runs: dict[str, pd.DataFrame]) -> go.Figure:
    fig = go.Figure()
    for i, (name, frame) in enumerate(runs.items()):
        fig.add_trace(go.Box(x=frame["predicted_good_gap"], name=name, boxpoints="all", jitter=0.5, pointpos=0,
                             marker=dict(color=[GREEN, AMBER][i % 2], size=6, opacity=.75), line=dict(color=INK)))
    fig.add_vline(x=0, line=dict(color=MUTED, dash="dot"))
    fig.update_xaxes(title="Under 25 minus 25 or older: share classified Good (percentage points)", tickformat=".0%")
    return style(fig, 300)
