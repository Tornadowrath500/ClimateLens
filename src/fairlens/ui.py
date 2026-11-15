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
from fairlens.demo import make_demo_dataset
from fairlens.evaluation import Audit, OperatingPoint, run_audit
from fairlens.models import MODEL_NAMES

INK, GREEN, SAGE, AMBER, MUTED, LINE = "#e6f1ff", "#42ddb3", "#82a9b2", "#f2b84b", "#9aacc2", "#263c54"
YOUNG, OLD = group_labels(AGE_GROUP_CUTOFF)
GROUP_COLOR = {YOUNG: AMBER, OLD: GREEN}
PROFILE_ACCENTS = {
    "Mint": ("#42ddb3", "#61c9ff"),
    "Sky": ("#61c9ff", "#9b8cff"),
    "Amber": ("#f2b84b", "#61c9ff"),
    "Violet": ("#b39aff", "#61c9ff"),
}

METRIC_HELP = {
    "accuracy": "Share of all applicants the model labelled correctly. Misleading when errors cost different amounts.",
    "recall_good": "Of applicants whose label is Good, the share the model also called Good. High means few good-risk people are turned away.",
    "recall_bad": "Of applicants whose label is Bad, the share the model correctly called Bad. This is how many risky cases it catches.",
    "precision_good": "Of applicants the model called Good, the share who really are labelled Good. Low means many 'Good' calls are mistakes.",
    "f1": "A single balance of precision and recall for the Good class. It ignores the 5-to-1 cost, so read it alongside cost.",
    "cost": "Average UCI cost per applicant: 5 for each Bad case called Good, 1 for each Good case called Bad. Lower is better.",
    "auc": "How well the model ranks Good above Bad cases regardless of threshold. 0.5 is a coin flip, 1.0 is perfect ranking.",
}

CSS = """
<style>
:root { color-scheme: dark; --fl-bg: #07111f; --fl-panel: #0c1a2b; --fl-panel-2: #102239;
  --fl-ink: #e6f1ff; --fl-muted: #9aacc2; --fl-line: #263c54; --fl-mint: #42ddb3; --fl-cyan: #61c9ff; --fl-amber: #f2b84b; }
html, body, .stApp, [data-testid="stMarkdownContainer"] { font-family: Inter, "Segoe UI", system-ui, sans-serif; }
html, body, .stApp { background: #07111f; color: var(--fl-ink); }
.stApp { background-image: radial-gradient(ellipse at 70% -15%, rgba(42, 116, 143, .19), transparent 42%),
  radial-gradient(ellipse at 5% 42%, rgba(36, 110, 101, .12), transparent 38%), linear-gradient(180deg, #07111f 0%, #091727 48%, #07111f 100%); }
.stApp::before { content: ""; position: fixed; inset: 0; z-index: 0; pointer-events: none; opacity: .28;
  background-image: linear-gradient(rgba(97,201,255,.16) 1px, transparent 1px), linear-gradient(90deg, rgba(97,201,255,.16) 1px, transparent 1px);
  background-size: 44px 44px; animation: fl-grid-drift 36s linear infinite; mask-image: linear-gradient(to bottom, black, transparent 88%); }
.stApp::after { content: ""; position: fixed; inset: -100% 0 auto; height: 32vh; z-index: 0; pointer-events: none;
  background: linear-gradient(transparent, rgba(66,221,179,.045), transparent); animation: fl-scan 18s linear infinite; }
@keyframes fl-grid-drift { to { background-position: 0 22px, 22px 0; } }
@keyframes fl-scan { to { transform: translateY(450vh); } }
.block-container { position: relative; z-index: 1; max-width: 1240px; padding-top: 2.4rem; padding-bottom: 4rem; }
header[data-testid="stHeader"] { background: rgba(7,17,31,.72); }
section[data-testid="stSidebar"] { position: relative; z-index: 1; background: linear-gradient(180deg, rgba(11,27,45,.98), rgba(7,17,31,.98)); border-right: 1px solid var(--fl-line); }
[data-testid="stSidebarNav"] { padding: .6rem .55rem 1rem; }
[data-testid="stSidebarNav"] li div[data-testid="stMarkdownContainer"] p { color: #9aacc2; font: 700 .78rem/1.35 Inter, "Segoe UI", system-ui, sans-serif; letter-spacing: .045em; }
[data-testid="stSidebarNavLink"] { box-sizing: border-box; min-height: 2.65rem; display: flex; align-items: center; border: 1px solid transparent; border-radius: 10px; margin: 3px 0; padding: .42rem .62rem; transition: background .2s ease, border-color .2s ease; }
[data-testid="stSidebarNavLink"]:hover { background: rgba(66,221,179,.09); }
[data-testid="stSidebarNavLink"] p { font-size: .98rem; line-height: 1.3; letter-spacing: .01em; font-weight: 560; }
h1, h2, h3, h4 { color: var(--fl-ink); letter-spacing: -.025em; font-weight: 650; }
h1 { font-size: clamp(2.1rem, 4vw, 3.25rem) !important; line-height: 1.1; }
h2 { line-height: 1.2; }
.fl-lede { color: var(--fl-muted); font-size: 1.08rem; line-height: 1.7; max-width: 52rem; margin: .25rem 0 1.4rem; }
.fl-eyebrow, .fl-section-kicker { color: var(--fl-cyan); font: 650 .68rem/1.4 ui-monospace, Consolas, monospace; letter-spacing: .15em; }
.fl-section-kicker { margin: 2.2rem 0 .45rem; }
.fl-pulse { display: inline-block; width: .5rem; height: .5rem; margin-right: .45rem; border-radius: 50%; background: var(--fl-mint); box-shadow: 0 0 14px rgba(66,221,179,.9); }
.fl-hero { position: relative; overflow: hidden; border: 1px solid rgba(97,201,255,.24); border-radius: 20px; padding: clamp(1.45rem, 4vw, 3rem);
  margin: .2rem 0 1.25rem; background: linear-gradient(120deg, rgba(13,34,55,.97), rgba(10,29,45,.82) 58%, rgba(13,53,60,.62));
  box-shadow: 0 20px 70px rgba(0,0,0,.22), inset 0 1px rgba(255,255,255,.04); }
.fl-hero::after { content: "◈"; position: absolute; right: 4%; top: 50%; transform: translateY(-50%); color: rgba(97,201,255,.08); font-size: clamp(8rem, 23vw, 19rem); line-height: 1; pointer-events: none; }
.fl-hero h1 { position: relative; z-index: 1; max-width: 48rem; margin: .65rem 0 .6rem; }
.fl-hero p { position: relative; z-index: 1; color: #bacadd; max-width: 48rem; margin: 0; font-size: 1.04rem; line-height: 1.7; }
.fl-hero-meta { display: flex; flex-wrap: wrap; gap: .65rem 1.4rem; margin-top: 1.5rem; color: #7899b2; font: 600 .65rem/1.4 ui-monospace, Consolas, monospace; letter-spacing: .12em; }
.fl-callout { border: 1px solid var(--fl-line); border-left: 3px solid var(--fl-mint); background: rgba(12,26,43,.88); border-radius: 10px; padding: .9rem 1.1rem; margin: .65rem 0 1.1rem; color: var(--fl-ink); line-height: 1.65; }
.fl-callout.caution { border-left-color: var(--fl-amber); }
.fl-callout strong { display: block; margin-bottom: .2rem; }
.fl-card { box-sizing: border-box; min-height: 196px; border: 1px solid var(--fl-line); border-radius: 14px; padding: 1rem 1.05rem; margin-bottom: .55rem;
  background: linear-gradient(145deg, rgba(16,34,57,.92), rgba(10,25,41,.93)); box-shadow: inset 0 1px rgba(255,255,255,.025); transition: transform .2s ease, border-color .2s ease, box-shadow .2s ease; }
.fl-card:hover { transform: translateY(-3px); border-color: rgba(66,221,179,.48); box-shadow: 0 12px 28px rgba(0,0,0,.2); }
.fl-card .fl-card-id { color: var(--fl-cyan); font: 650 .65rem/1.2 ui-monospace, Consolas, monospace; letter-spacing: .13em; }
.fl-card h4 { margin: .55rem 0 .38rem; font-size: 1.04rem; }
.fl-card p { color: var(--fl-muted); margin: 0; font-size: .89rem; line-height: 1.55; }
.fl-flow { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: .65rem; }
.fl-flow-step { min-width: 0; display: flex; flex-direction: column; gap: .38rem; padding: .85rem .9rem; border: 1px solid var(--fl-line); border-radius: 12px; background: rgba(12,26,43,.7); }
.fl-flow-step span { color: var(--fl-mint); font: 650 .66rem/1.3 ui-monospace, Consolas, monospace; }
.fl-flow-step strong { font-size: .9rem; }
.fl-flow-step small { color: var(--fl-muted); line-height: 1.45; }
.fl-health-panel { display: grid; grid-template-columns: 2.4rem minmax(0,1fr); gap: 1rem; padding: clamp(1rem,3vw,1.5rem); border: 1px solid rgba(97,201,255,.2); border-radius: 16px; background: linear-gradient(120deg, rgba(14,33,53,.94), rgba(11,27,44,.82)); }
.fl-health-icon { display: grid; place-items: center; width: 2.2rem; height: 2.2rem; border: 1px solid rgba(66,221,179,.4); border-radius: 10px; color: var(--fl-mint); box-shadow: 0 0 24px rgba(66,221,179,.1); }
.fl-health-panel h3 { margin: .25rem 0 .5rem; font-size: 1.22rem; }
.fl-health-panel p { color: #b5c5d7; line-height: 1.65; }
.fl-health-panel .fl-limit { padding: .8rem .9rem; border-left: 2px solid var(--fl-amber); border-radius: 0 8px 8px 0; background: rgba(242,184,75,.06); font-size: .9rem; }
.fl-health-panel a { color: var(--fl-cyan); text-decoration: none; }
.fl-health-panel a:hover { text-decoration: underline; }
.fl-source-sep { color: var(--fl-muted); margin: 0 .5rem; }
.fl-step { display: flex; gap: 1rem; padding: .85rem 0; border-top: 1px solid var(--fl-line); }
.fl-step:last-child { border-bottom: 1px solid var(--fl-line); }
.fl-step b { font: 650 1.4rem/1.2 ui-monospace, Consolas, monospace; color: var(--fl-mint); min-width: 1.6rem; }
.fl-step span, .stCaption, [data-testid="stCaptionContainer"] { color: var(--fl-muted); }
.fl-group { border: 1px solid var(--fl-line); border-radius: 10px; padding: .9rem 1.1rem; background: var(--fl-panel); }
.fl-group .n { font: 650 2rem/1.1 ui-monospace, Consolas, monospace; color: var(--fl-ink); }
[data-testid="stMetric"] { background: linear-gradient(145deg, rgba(16,34,57,.94), rgba(10,25,41,.94)); border: 1px solid var(--fl-line); border-radius: 12px; padding: .75rem .9rem; }
[data-testid="stMetricValue"] { color: var(--fl-ink); }
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 1px solid var(--fl-line); border-radius: 10px; overflow: hidden; }
.fl-chip { display: inline-block; padding: .14rem .62rem; border-radius: 999px; font-size: .78rem; font-weight: 650; margin-right: .35rem; border: 1px solid var(--fl-line); background: var(--fl-panel-2); color: var(--fl-ink); }
.fl-chip.good { background: rgba(66,221,179,.12); color: #83f1d3; border-color: rgba(66,221,179,.38); }
.fl-chip.bad { background: rgba(242,184,75,.12); color: #ffd27a; border-color: rgba(242,184,75,.36); }
.fl-chip.demo { background: rgba(242,184,75,.12); color: #ffd27a; border-color: rgba(242,184,75,.36); }
.fl-bar { position: relative; height: 16px; border-radius: 8px; background: linear-gradient(90deg, #b7791f, #31445a 50%, #42ddb3); border: 1px solid var(--fl-line); margin: .6rem 0 1.5rem; }
.fl-bar i { position: absolute; top: -5px; width: 4px; height: 24px; background: var(--fl-ink); border-radius: 2px; box-shadow: 0 0 7px rgba(230,241,255,.7); }
.fl-bar u { position: absolute; top: -5px; width: 0; height: 24px; border-left: 2px dashed var(--fl-amber); text-decoration: none; }
.fl-bar span { position: absolute; top: 20px; font-size: .72rem; color: var(--fl-muted); transform: translateX(-50%); white-space: nowrap; }
[data-testid="stBaseButton-primary"] { box-shadow: 0 0 24px rgba(66,221,179,.12); }
button, input, textarea, [role="combobox"] { border-radius: 9px !important; }
:focus-visible { outline: 2px solid var(--fl-cyan) !important; outline-offset: 2px !important; }
@media (max-width: 850px) { .fl-flow { grid-template-columns: repeat(2, minmax(0,1fr)); } .fl-flow-step:last-child { grid-column: 1 / -1; } }
@media (max-width: 520px) { .block-container { padding-top: 1.3rem; } .fl-health-panel { grid-template-columns: 1fr; } .fl-flow { grid-template-columns: 1fr 1fr; } .fl-hero-meta { gap: .45rem .8rem; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation: none !important; transition: none !important; scroll-behavior: auto !important; } }

/* Streamlit shell refinement: align native page icons and keep appearance controls legible. */
[data-testid="stSidebarNavLink"] { display:flex !important; align-items:center !important; gap:.65rem !important; padding:.48rem .72rem !important; }
[data-testid="stSidebarNavLink"] > span:first-child { width:1.35rem !important; min-width:1.35rem !important; display:inline-flex !important; align-items:center !important; justify-content:center !important; margin:0 !important; opacity:1 !important; }
[data-testid="stSidebarNavLink"] [data-testid="stMarkdownContainer"] { display:flex !important; align-items:center !important; min-height:1.5rem !important; }
[data-testid="stSidebarNavLink"] p { margin:0 !important; line-height:1.35 !important; text-align:left !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] { border-color:rgba(66,221,179,.42) !important; background:rgba(66,221,179,.12) !important; }
[data-testid="stSidebar"] [data-testid="stToggle"] { padding:.45rem .65rem !important; border:1px solid var(--fl-line) !important; border-radius:10px !important; background:var(--fl-panel) !important; }
[data-testid="stSidebar"] [data-testid="stToggle"] label,
[data-testid="stSidebar"] [data-testid="stToggle"] label p { color:var(--fl-ink) !important; font-weight:650 !important; opacity:1 !important; }
[data-testid="stSidebar"] [data-testid="stToggle"] [role="switch"] { opacity:1 !important; }
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"] { color:#61c9ff; }
[data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stIconMaterial"] { color:#42ddb3; }
/* Identity layer: animated hero edge, gradient headline, scope ribbon, audit-route tracker. */
@property --fl-angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
.fl-hero { border: 1px solid transparent; background: linear-gradient(120deg, rgba(13,34,55,.97), rgba(10,29,45,.9) 58%, rgba(13,53,60,.8)) padding-box,
  conic-gradient(from var(--fl-angle), rgba(97,201,255,.7), rgba(66,221,179,.15), rgba(155,140,255,.5), rgba(97,201,255,.7)) border-box; animation: fl-spin 14s linear infinite; }
@keyframes fl-spin { to { --fl-angle: 360deg; } }
.fl-hero h1 { background: linear-gradient(95deg, #f2f8ff 20%, #8fdcff 60%, #7ff0d0); -webkit-background-clip: text; background-clip: text; color: transparent !important; }
.fl-card::before { content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none; opacity: 0; transition: opacity .25s;
  background: radial-gradient(circle at 20% 0%, rgba(97,201,255,.16), transparent 60%); }
.fl-card { position: relative; } .fl-card:hover::before { opacity: 1; }
.fl-scope { display: flex; flex-wrap: wrap; align-items: center; gap: .5rem .8rem; margin: -.6rem 0 1rem; font-size: .8rem; color: var(--fl-muted); }
.fl-scope .fl-chip { margin: 0; }
.fl-route { margin: .4rem .2rem 1rem; padding: .8rem .85rem; border: 1px solid var(--fl-line); border-radius: 12px; background: var(--fl-panel); }
.fl-route b { display: block; font: 650 .66rem/1.3 ui-monospace, Consolas, monospace; letter-spacing: .14em; color: var(--fl-cyan); margin-bottom: .5rem; }
.fl-route-track { height: 5px; border-radius: 3px; background: var(--fl-line); overflow: hidden; margin-bottom: .55rem; }
.fl-route-track i { display: block; height: 100%; background: linear-gradient(90deg, var(--fl-cyan), var(--fl-mint)); transition: width .4s ease; }
.fl-route ol { list-style: none; margin: 0; padding: 0; font-size: .82rem; line-height: 1.9; color: var(--fl-ink); }
.fl-route li.done { color: var(--fl-mint); } .fl-route li::before { content: "○  "; opacity: .6; } .fl-route li.done::before { content: "✓  "; opacity: 1; font-weight: 700; }
/* Polish layer: depth, motion, typography. Uses theme variables so both modes inherit it. */
::selection { background: rgba(66,221,179,.3); }
* { scrollbar-width: thin; scrollbar-color: var(--fl-line) transparent; }
.block-container { animation: fl-rise .55s cubic-bezier(.2,.8,.2,1) both; }
@keyframes fl-rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
header[data-testid="stHeader"] { backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); }
h2 { position: relative; padding-bottom: .35rem; }
h2::after { content: ""; position: absolute; left: 0; bottom: 0; width: 2.6rem; height: 2px; border-radius: 2px; background: linear-gradient(90deg, var(--fl-cyan), var(--fl-mint)); }
.fl-callout { backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px); box-shadow: 0 8px 28px rgba(0,0,0,.12); }
[data-testid="stMetric"] { position: relative; overflow: hidden; transition: transform .2s ease, border-color .2s ease; }
[data-testid="stMetric"]::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: linear-gradient(180deg, var(--fl-cyan), var(--fl-mint)); }
[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color: var(--fl-mint); }
[data-testid="stMetricValue"] { font-family: ui-monospace, Consolas, monospace; letter-spacing: -.02em; }
[data-testid="stBaseButton-primary"] { background: linear-gradient(120deg, var(--fl-mint), var(--fl-cyan)) !important; border: 0 !important; color: #04131f !important; font-weight: 700; transition: transform .18s ease, box-shadow .18s ease; }
[data-testid="stBaseButton-primary"] p { color: #04131f !important; }
[data-testid="stBaseButton-primary"]:hover { transform: translateY(-1px); box-shadow: 0 8px 26px rgba(66,221,179,.35); }
[data-testid="stBaseButton-secondary"] { transition: transform .18s ease, border-color .18s ease; }
[data-testid="stBaseButton-secondary"]:hover { transform: translateY(-1px); border-color: var(--fl-mint) !important; }
[data-testid="stTabs"] [role="tablist"] { gap: .35rem; border-bottom: 1px solid var(--fl-line); }
[data-testid="stTabs"] [role="tab"] { border-radius: 9px 9px 0 0; padding: .45rem .9rem; transition: background .2s ease; }
[data-testid="stTabs"] [role="tab"]:hover { background: rgba(66,221,179,.09); }
[data-testid="stExpander"] { border-radius: 12px !important; border-color: var(--fl-line) !important; }
[data-testid="stPageLink-NavLink"] { border-radius: 9px; transition: background .2s ease, transform .2s ease; }
[data-testid="stPageLink-NavLink"]:hover { background: rgba(66,221,179,.1); transform: translateX(3px); }
.fl-stats { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: .65rem; margin: 0 0 1.2rem; }
.fl-stat { padding: .85rem 1rem; border: 1px solid var(--fl-line); border-radius: 14px; background: var(--fl-panel); position: relative; overflow: hidden; }
.fl-stat::after { content: ""; position: absolute; right: -1.2rem; top: -1.2rem; width: 4rem; height: 4rem; border-radius: 50%; background: radial-gradient(circle, rgba(97,201,255,.22), transparent 70%); }
.fl-stat b { display: block; font: 650 1.7rem/1.1 ui-monospace, Consolas, monospace; color: var(--fl-mint); letter-spacing: -.03em; }
.fl-stat span { display: block; margin-top: .25rem; color: var(--fl-muted); font-size: .8rem; line-height: 1.4; }
.fl-verdict { border-radius: 14px; padding: 1rem 1.2rem; margin: .4rem 0 1rem; border: 1px solid var(--fl-line); background: var(--fl-panel); }
.fl-verdict .fl-meter { height: 8px; border-radius: 4px; background: var(--fl-line); overflow: hidden; margin: .55rem 0; }
.fl-verdict .fl-meter i { display: block; height: 100%; background: linear-gradient(90deg, var(--fl-amber), var(--fl-mint)); transition: width .4s ease; }
@media (max-width: 850px) { .fl-stats { grid-template-columns: repeat(2, minmax(0,1fr)); } }

.fl-dashboard-callout { display:grid; grid-template-columns:minmax(0,1.15fr) minmax(17rem,.85fr); gap:1.5rem; align-items:center; padding:1.35rem 1.5rem; margin:.4rem 0 1.4rem; border:1px solid rgba(97,201,255,.3); border-radius:16px; background:linear-gradient(115deg,rgba(12,36,54,.96),rgba(14,61,64,.72)); box-shadow:0 16px 44px rgba(0,0,0,.16),inset 0 1px rgba(255,255,255,.04); }
.fl-dashboard-callout h3 { margin:.35rem 0; font-size:1.3rem; }
.fl-dashboard-callout p { margin:0; color:var(--fl-muted); line-height:1.55; }
@media(max-width:760px) { .fl-dashboard-callout { grid-template-columns:1fr; } }
/* Over-claim statement card, hero scan line, glossary tooltips. */
.fl-hero::before { content: ""; position: absolute; inset: 0; pointer-events: none; background: linear-gradient(100deg, transparent 38%, rgba(97,201,255,.11) 50%, transparent 62%); transform: translateX(-100%); animation: fl-scan 7s ease-in-out infinite; }
@keyframes fl-scan { 60%, 100% { transform: translateX(100%); } }
.fl-term { position: relative; display: inline-block; margin: .15rem .3rem .15rem 0; padding: .2rem .65rem; border: 1px dashed var(--fl-cyan); border-radius: 999px; font-size: .82rem; color: var(--fl-ink); cursor: help; }
.fl-term::after { content: attr(data-tip); position: absolute; left: 0; top: calc(100% + 8px); width: 15rem; padding: .6rem .75rem; border-radius: 10px; border: 1px solid var(--fl-line); background: var(--fl-panel); color: var(--fl-ink); font-size: .78rem; line-height: 1.45; box-shadow: 0 10px 30px rgba(0,0,0,.25); opacity: 0; transform: translateY(-4px); pointer-events: none; transition: opacity .18s ease, transform .18s ease; z-index: 20; }
.fl-term:focus-visible { outline: 2px solid var(--fl-mint); outline-offset: 2px; }
.fl-term:hover::after, .fl-term:focus::after { opacity: 1; transform: none; }
/* Trust footer, print, small screens, cost explorer. */
.block-container::after { content: "FairLens is an educational audit tool. Results describe historical, synthetic or user-provided data, not current people, patients or lenders, and are not legal, financial or medical advice."; display: block; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--fl-line); color: var(--fl-muted); font-size: .76rem; line-height: 1.5; }
.fl-terms { margin: .2rem 0 1rem; } .fl-terms-label { margin-right: .6rem; font: 650 .66rem/1 ui-monospace, Consolas, monospace; letter-spacing: .14em; text-transform: uppercase; color: var(--fl-muted); }
.fl-stat-text { font-size: 1.05rem !important; line-height: 1.5 !important; letter-spacing: 0 !important; }
.fl-costbar { display: flex; height: 18px; border-radius: 9px; overflow: hidden; background: var(--fl-line); margin: .4rem 0 .5rem; }
.fl-costbar i { display: block; height: 100%; transition: width .45s cubic-bezier(.2,.8,.2,1); } .fl-costbar .a { background: linear-gradient(90deg, var(--fl-amber), #ff8a5c); } .fl-costbar .b { background: linear-gradient(90deg, var(--fl-cyan), var(--fl-mint)); }
.fl-costkey { display: flex; flex-wrap: wrap; gap: .4rem 1.4rem; margin-bottom: .6rem; font-size: .84rem; color: var(--fl-ink); } .fl-costkey b { display: inline-block; width: .7rem; height: .7rem; border-radius: 3px; margin-right: .45rem; } .fl-costkey b.a { background: var(--fl-amber); } .fl-costkey b.b { background: var(--fl-cyan); }
@media (max-width: 640px) { .fl-hero { padding: 1.4rem 1.1rem; } .fl-hero h1 { font-size: 1.9rem; } .fl-stats { grid-template-columns: 1fr 1fr; } .fl-term::after { width: 12rem; } }
@media print {
  [data-testid="stSidebar"], header[data-testid="stHeader"], [data-testid="stSidebarCollapsedControl"], [data-testid="stToolbar"], .fl-hero::before { display: none !important; }
  .stApp, .block-container { background: #fff !important; color: #111 !important; animation: none !important; } .block-container { max-width: 100% !important; padding: 0 1rem !important; }
  * { color: #111 !important; box-shadow: none !important; } .fl-hero, .fl-card, .fl-callout, [data-testid="stMetric"] { border-color: #bbb !important; background: #fff !important; break-inside: avoid; }
}
.fl-statement { font-size: 1.25rem; line-height: 1.5; padding: 1.4rem 1.5rem; border: 1px solid var(--fl-line); border-left: 4px solid var(--fl-cyan); border-radius: 14px; background: var(--fl-panel); margin: .6rem 0 1rem; color: var(--fl-ink); animation: fl-rise .4s both; }
</style>
"""

LIGHT_MODE_CSS = """
<style>
:root { color-scheme: light; --fl-bg:#f2f6f8; --fl-panel:#fff; --fl-panel-2:#e7eff3;
  --fl-ink:#172b3b; --fl-muted:#526b7e; --fl-line:#cbd9e2; --fl-mint:#087e68; --fl-cyan:#176b92; --fl-amber:#98620b; }
html, body, .stApp { background:#f2f6f8; color:var(--fl-ink); }
.stApp [data-testid="stMarkdownContainer"], .stApp label, .stApp [data-testid="stWidgetLabel"] p,
.stApp [data-testid="stMetricLabel"], .stApp [data-testid="stMetricValue"] { color:var(--fl-ink); }
.stApp [data-testid="stCaptionContainer"], .stApp .stCaption { color:var(--fl-muted); }
.stApp { background-image:radial-gradient(ellipse at 75% -15%,rgba(38,145,171,.13),transparent 42%),
  radial-gradient(ellipse at 5% 42%,rgba(29,141,112,.08),transparent 38%),linear-gradient(180deg,#f5f8fa 0%,#edf3f6 52%,#f2f6f8 100%); }
.stApp::before { opacity:.16; background-image:linear-gradient(rgba(23,107,146,.15) 1px,transparent 1px),linear-gradient(90deg,rgba(23,107,146,.15) 1px,transparent 1px); }
.stApp::after { background:linear-gradient(transparent,rgba(8,126,104,.035),transparent); }
header[data-testid="stHeader"] { background:rgba(242,246,248,.82); }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#f9fbfc,#eaf1f4); border-right-color:var(--fl-line); }
[data-testid="stSidebarNav"] li div[data-testid="stMarkdownContainer"] p { color:#526b7e; }
[data-testid="stSidebarNavLink"] { color:#243b4d; }
[data-testid="stSidebarNavLink"]:hover { background:rgba(8,126,104,.09); border-color:rgba(8,126,104,.18); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background:#dceee9; border-color:#b6d9cf; }
h1,h2,h3,h4 { color:var(--fl-ink); }
.fl-eyebrow,.fl-section-kicker { color:#176b92; }
.fl-hero { background:linear-gradient(120deg,#17334a,#19465a 58%,#17645b); }
.fl-callout { background:rgba(255,255,255,.9); }
.fl-card { background:linear-gradient(145deg,#fff,#f3f7f9); box-shadow:0 8px 24px rgba(29,58,77,.06); }
.fl-flow-step { background:rgba(255,255,255,.86); }
.fl-health-panel { background:linear-gradient(120deg,#fff,#edf5f6); }
.fl-health-panel p { color:#40596c; }
.fl-health-panel .fl-limit { background:rgba(152,98,11,.07); }
[data-testid="stMetric"] { background:linear-gradient(145deg,#fff,#f3f7f9); }
.fl-chip { color:#172b3b; }
.fl-chip.good { color:#075d4d; background:#d9f2e9; }
.fl-chip.bad,.fl-chip.demo { color:#744900; background:#fff0d2; }
.fl-bar i { background:#172b3b; box-shadow:0 0 7px rgba(23,43,59,.3); }
.fl-bar span { color:#40596c; }
button, input, textarea, [role="combobox"] { color:var(--fl-ink); }
[data-testid="stMetricValue"], [data-testid="stMetricLabel"], [data-testid="stWidgetLabel"] { color:var(--fl-ink); }
/* Sidebar icons: dark ink on light surfaces, in tinted tiles so they never vanish. */
section[data-testid="stSidebar"], section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] summary { color:#243b4d; }
[data-testid="stSidebarNavLink"] [data-testid="stIconMaterial"], [data-testid="stSidebarNavLink"] span[class*="material"],
[data-testid="stSidebarNavLink"] > span:first-child { color:#176b92 !important; fill:#176b92 !important; opacity:1 !important;
  background:rgba(23,107,146,.10); border-radius:8px; padding:.14rem; box-sizing:content-box; }
[data-testid="stSidebarNavLink"][aria-current="page"] [data-testid="stIconMaterial"],
[data-testid="stSidebarNavLink"][aria-current="page"] > span:first-child { color:#fff !important; background:#087e68; }
[data-testid="stSidebarNavLink"] p { color:#243b4d !important; }
[data-testid="stSidebarNavLink"][aria-current="page"] p { color:#064c3f !important; font-weight:700; }
header[data-testid="stHeader"] button, header[data-testid="stHeader"] [data-testid="stIconMaterial"],
[data-testid="stSidebarCollapseButton"] button, [data-testid="stExpandSidebarButton"] { color:#243b4d !important; }
[data-testid="stSidebar"] [data-testid="stToggle"] { background:#fff !important; border-color:#cbd9e2 !important; }
[data-testid="stSidebar"] [data-testid="stToggle"] label p { color:#172b3b !important; }
.stApp [data-baseweb="select"] > div, .stApp input, .stApp textarea { background:#fff !important; color:#172b3b !important; }
.stApp [data-testid="stExpander"] { background:#fff; border-color:#cbd9e2; }
.stApp [data-testid="stExpander"] summary, .stApp [data-testid="stExpander"] summary * { color:#172b3b !important; }
.stApp [data-testid="stVerticalBlockBorderWrapper"] { border-color:#cbd9e2; }
.stApp [role="tab"], .stApp [data-testid="stTabs"] button p { color:#243b4d !important; }
.stApp [data-testid="stBaseButton-secondary"] { background:#fff; color:#172b3b; border-color:#b8cad6; }
.stApp [data-testid="stBaseButton-secondary"] p { color:#172b3b !important; }
.stApp [data-testid="stPageLink-NavLink"] p, .stApp [data-testid="stPageLink-NavLink"] span { color:#176b92 !important; }
.stApp .fl-hero h1, .stApp .fl-hero p { color:#eef6ff; }
.stApp .fl-hero .fl-eyebrow { color:#8fdcff; }
</style>
"""


ROUTE = [  # (label, page titles that complete the step)
    ("Data and scope", {"Understand the data"}, "pages/1_Understand_the_Data.py"),
    ("Model performance", {"Evaluate the model"}, "pages/2_Evaluate_the_Model.py"),
    ("Group outcomes", {"Investigate group outcomes"}, "pages/3_Investigate_Group_Outcomes.py"),
    ("A what-if test", {"Experiment lab", "Mitigation lab", "Applicant simulator", "Proxy detector", "Applicant map"}, "pages/4_Experiment_Lab.py"),
    ("Findings and limits", {"Findings and report", "Methodology and limitations", "Claim checker"}, "pages/5_Findings_and_Report.py"),
]
_SYNTHETIC_PAGES = {"Health equity lab"}
_NO_RIBBON = {"Over-claim game", "Claim checker", "Home", "Session profile", "Your first FairLens tour", "Methodology and limitations"}


JUMP = [
    ("Home", "pages/0_Home.py"), ("Take the tour", "pages/13_Tutorial.py"), ("Data & scope", "pages/1_Understand_the_Data.py"),
    ("Model performance", "pages/2_Evaluate_the_Model.py"), ("Group outcomes", "pages/3_Investigate_Group_Outcomes.py"),
    ("Findings & report", "pages/5_Findings_and_Report.py"), ("Claim checker", "pages/15_Claim_Checker.py"),
    ("Methods & limits", "pages/6_Methodology_and_Limitations.py"), ("Hidden bias challenge", "pages/14_Hidden_Bias_Challenge.py"),
    ("Over-claim game", "pages/17_Overclaim_Game.py"), ("Applicant map", "pages/7_Applicant_Map.py"),
    ("Applicant simulator", "pages/8_Applicant_Simulator.py"), ("Proxy detector", "pages/9_Proxy_Detector.py"),
    ("Experiment lab", "pages/4_Experiment_Lab.py"), ("Mitigation lab", "pages/10_Mitigation_Lab.py"),
    ("Audit your model", "pages/11_Audit_Your_Model.py"), ("Health lab (synthetic)", "pages/14_Health_Equity_Lab.py"),
]


def _jump_cb() -> None:
    pick = st.session_state.get("fl_jump")
    if pick:
        st.session_state["fl_jump_target"] = dict(JUMP)[pick]
        st.session_state["fl_jump"] = None


def _jump_box() -> None:
    """Type-ahead page finder: a lightweight command palette for the sidebar."""
    target = st.session_state.pop("fl_jump_target", None)
    if target:
        st.switch_page(target)
    st.selectbox("Quick jump", [t for t, _ in JUMP], index=None, placeholder="⌕  Jump to any page…", key="fl_jump",
                 on_change=_jump_cb, label_visibility="collapsed")


PAGE_META = {  # setup_page title -> (nav group, short label) for the top breadcrumb
    "Session profile": ("START", "Profile"), "Your first FairLens tour": ("START", "Tour"),
    "Understand the data": ("REVIEW", "Data &amp; scope"), "Evaluate the model": ("REVIEW", "Model performance"),
    "Investigate group outcomes": ("REVIEW", "Group outcomes"), "Findings and report": ("REVIEW", "Findings"),
    "Claim checker": ("REVIEW", "Claim checker"), "Methodology and limitations": ("REVIEW", "Methods &amp; limits"),
    "Hidden bias challenge": ("TRY IT", "Bias challenge"), "Over-claim game": ("TRY IT", "Over-claim game"),
    "Applicant map": ("EXPLORE", "Applicant map"), "Applicant simulator": ("EXPLORE", "Simulator"),
    "Proxy detector": ("EXPLORE", "Proxy detector"), "Experiment lab": ("EXPLORE", "Experiment lab"),
    "Mitigation lab": ("EXPLORE", "Mitigation lab"), "Audit your own model": ("EXPLORE", "Your model"),
    "Health equity lab": ("EXPLORE", "Health lab · synthetic"),
}


def _track_route(title: str) -> None:
    """Remember visited pages, show a scope ribbon, and draw the sidebar audit-route tracker."""
    visited = st.session_state.setdefault("fl_visited", set())
    visited.add(title)
    if title in _SYNTHETIC_PAGES:
        chip = '<span class="fl-chip demo">SYNTHETIC SIMULATION</span>Invented records: not patient data, not evidence, not health advice.'
    elif title == "Audit your own model":
        chip = '<span class="fl-chip">YOUR DATA</span>Processed in this session only. Results describe your file, not any wider population.'
    elif title in _NO_RIBBON:
        chip = ""
    elif st.session_state.get("use_demo_data") and not dataset_path().exists():
        chip = '<span class="fl-chip demo">SYNTHETIC DEMO DATA</span>Invented German-Credit-style records for offline exploration.'
    else:
        chip = '<span class="fl-chip">HISTORICAL BENCHMARK</span>UCI German Credit (1994). Educational only; not today\'s applicants or lenders.'
    done = [bool(pages & visited) for _, pages, _ in ROUTE]
    nxt = next(((label, path) for (label, _, path), d in zip(ROUTE, done) if not d), None)
    meta = PAGE_META.get(title)
    if meta:
        left, right = st.columns([3, 2], vertical_alignment="center")
        left.markdown(
            f'<div class="fl-hud">FairLens<i>/</i>{meta[0]}<i>/</i><b>{meta[1]}</b><span class="fl-cursor"></span></div>',
            unsafe_allow_html=True,
        )
        if nxt:
            # AppTest can render a page module outside the registered multipage app.
            # In that isolated context, keep route guidance visible without asking
            # Streamlit to resolve a page that is not registered in the test runner.
            try:
                right.page_link(nxt[1], label=f"Next in the route: {nxt[0]}", icon=":material/arrow_forward:")
            except st.errors.StreamlitAPIException:
                right.caption(f"Next in the route: {nxt[0]}")
    if chip:
        st.markdown(f'<div class="fl-scope">{chip}</div>', unsafe_allow_html=True)
    items = "".join(f'<li class="{"done" if d else ""}">{label}</li>' for (label, _, _), d in zip(ROUTE, done))
    pct = 100 * sum(done) // len(ROUTE)
    with st.sidebar:
        _jump_box()
        st.markdown(
            f'<div class="fl-route" role="group" aria-label="Audit route progress"><b>AUDIT ROUTE · {sum(done)}/{len(ROUTE)}</b>'
            f'<div class="fl-route-track"><i style="width:{pct}%"></i></div><ol>{items}</ol></div>',
            unsafe_allow_html=True,
        )
        if not nxt:
            st.caption("Route complete. Try the Claim checker or the Health lab next.")


FUTURE_CSS = """
<style>
/* FUTURE layer: HUD corners, staggered entrances, signal lines, ambient motion. Loaded after the base and light skins. */
@keyframes fl-fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes fl-run { from { background-position: -70% 0; } to { background-position: 170% 0; } }
@keyframes fl-blink { 50% { opacity: 0; } }
@keyframes fl-float { 50% { transform: translateY(calc(-50% - 9px)) rotate(10deg); } }
@keyframes fl-ring { 0%, 100% { box-shadow: 0 0 0 0 rgba(66,221,179,.0); } 50% { box-shadow: 0 0 0 7px rgba(66,221,179,.16); } }
@keyframes fl-sweep { to { background-position: -200% 0; } }

/* HUD corner brackets */
.fl-card, .fl-callout, .fl-stat, [data-testid="stMetric"] { position: relative; }
.fl-card::after, .fl-callout::after, .fl-stat::before, [data-testid="stMetric"]::after {
  content: ""; position: absolute; inset: -1px; border-radius: inherit; pointer-events: none; opacity: .5;
  --b: var(--fl-cyan); transition: opacity .25s ease, inset .25s ease;
  background:
    linear-gradient(var(--b), var(--b)) 0 0 / 14px 2px no-repeat, linear-gradient(var(--b), var(--b)) 0 0 / 2px 14px no-repeat,
    linear-gradient(var(--b), var(--b)) 100% 0 / 14px 2px no-repeat, linear-gradient(var(--b), var(--b)) 100% 0 / 2px 14px no-repeat,
    linear-gradient(var(--b), var(--b)) 0 100% / 14px 2px no-repeat, linear-gradient(var(--b), var(--b)) 0 100% / 2px 14px no-repeat,
    linear-gradient(var(--b), var(--b)) 100% 100% / 14px 2px no-repeat, linear-gradient(var(--b), var(--b)) 100% 100% / 2px 14px no-repeat; }
.fl-card:hover::after, .fl-stat:hover::before, [data-testid="stMetric"]:hover::after, .fl-callout:hover::after { opacity: 1; inset: -3px; }
.fl-card { transition: transform .25s ease, box-shadow .25s ease; } .fl-card:hover { transform: translateY(-3px); box-shadow: 0 14px 34px rgba(0,0,0,.2); }

/* Staggered entrances (elements persist across reruns, so slider drags do not replay them) */
.fl-card, .fl-stat, .fl-flow-step, .fl-chip, .fl-hero-meta span { animation: fl-rise .65s cubic-bezier(.2,.8,.2,1) backwards; }
.fl-stat:nth-child(2), .fl-flow-step:nth-child(2), .fl-hero-meta span:nth-child(2) { animation-delay: .08s; }
.fl-stat:nth-child(3), .fl-flow-step:nth-child(3), .fl-hero-meta span:nth-child(3) { animation-delay: .16s; }
.fl-stat:nth-child(4), .fl-flow-step:nth-child(4) { animation-delay: .24s; } .fl-flow-step:nth-child(5) { animation-delay: .32s; }
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] { animation: fl-fade .8s ease both; }

/* Signal line travelling across each step of the audit route */
.fl-flow-step { position: relative; overflow: hidden; }
.fl-flow-step::before { content: ""; position: absolute; left: 0; top: 0; width: 100%; height: 2px; background: linear-gradient(90deg, transparent, var(--fl-mint), transparent) -70% 0 / 45% 100% no-repeat; animation: fl-run 3.6s linear infinite; }
.fl-flow-step:nth-child(2)::before { animation-delay: .5s; } .fl-flow-step:nth-child(3)::before { animation-delay: 1s; } .fl-flow-step:nth-child(4)::before { animation-delay: 1.5s; } .fl-flow-step:nth-child(5)::before { animation-delay: 2s; }
.fl-hero::after { animation: fl-float 7s ease-in-out infinite; }

/* Headlines, sidebar and controls */
h1 { background: linear-gradient(95deg, var(--fl-ink) 55%, var(--fl-cyan)); -webkit-background-clip: text; background-clip: text; color: transparent !important; }
.fl-lede { animation: fl-fade 1s .15s ease both; }
[data-testid="stSidebarNav"] { max-height: 50vh; overflow-y: auto; }
[data-testid="stSidebarNavLink"] { transition: transform .18s ease, background .18s ease, box-shadow .18s ease; }
[data-testid="stSidebarNavLink"]:hover { transform: translateX(3px); }
[data-testid="stSidebarNavLink"][aria-current="page"] { box-shadow: inset 3px 0 0 var(--fl-mint), 0 0 20px rgba(66,221,179,.16); }
[data-testid="stBaseButton-primary"] { animation: fl-ring 3.2s ease-in-out infinite; }
[data-testid="stSpinner"] { padding: .6rem .9rem; border: 1px solid var(--fl-line); border-radius: 12px; background: linear-gradient(90deg, var(--fl-panel) 30%, rgba(97,201,255,.16) 50%, var(--fl-panel) 70%) 0 0 / 200% 100%; animation: fl-sweep 1.6s linear infinite; }
[data-testid="stSlider"] [role="slider"] { box-shadow: 0 0 0 4px rgba(66,221,179,.18); transition: box-shadow .2s ease; } [data-testid="stSlider"] [role="slider"]:hover { box-shadow: 0 0 0 8px rgba(66,221,179,.22); }

/* Top HUD: breadcrumb with a blinking cursor */
.fl-hud { display: flex; align-items: center; flex-wrap: wrap; gap: .5rem; margin: -.4rem 0 .2rem; font: 650 .68rem/1.4 ui-monospace, Consolas, monospace; letter-spacing: .15em; text-transform: uppercase; color: var(--fl-muted); }
.fl-hud i { font-style: normal; opacity: .45; } .fl-hud b { color: var(--fl-cyan); }
.fl-cursor { width: .5rem; height: .95rem; margin-left: .15rem; background: var(--fl-mint); animation: fl-blink 1.1s steps(1) infinite; }
@media (max-width: 640px) { .fl-hud { font-size: .6rem; letter-spacing: .1em; } }
</style>
"""


def setup_page(title: str) -> None:
    """Inject the shared UI skin; app.py configures the Streamlit page once."""
    st.markdown(CSS, unsafe_allow_html=True)
    if st.session_state.get("fl_light_mode", False):
        st.markdown(LIGHT_MODE_CSS, unsafe_allow_html=True)
    st.markdown(FUTURE_CSS, unsafe_allow_html=True)
    _track_route(title)
    profile = st.session_state.get("fl_profile", {})
    accent, secondary = PROFILE_ACCENTS.get(profile.get("accent", "Mint"), PROFILE_ACCENTS["Mint"])
    st.markdown(
        f"<style>:root{{--fl-mint:{accent};--fl-cyan:{secondary};}}</style>",
        unsafe_allow_html=True,
    )


def theme_control() -> None:
    """Show an app-wide appearance switch; Streamlit session state persists it across pages."""
    if "fl_light_mode" not in st.session_state:
        st.session_state["fl_light_mode"] = False
    with st.sidebar:
        st.toggle("Light mode", key="fl_light_mode", help="Switch the app appearance for this session.")


def header(title: str, lede: str) -> None:
    st.title(title)
    st.markdown(f'<p class="fl-lede">{lede}</p>', unsafe_allow_html=True)


def callout(title: str, body: str, kind: str = "note") -> None:
    st.markdown(
        f'<div class="fl-callout {kind}"><strong>{title}</strong>{body}</div>', unsafe_allow_html=True
    )


def show_chart(fig: go.Figure) -> None:
    try:
        st.plotly_chart(fig, theme=None, width="stretch", config={"responsive": True, "displaylogo": False})
    except TypeError:  # older Streamlit
        st.plotly_chart(fig, theme=None, use_container_width=True, config={"responsive": True, "displaylogo": False})


def show_table(frame: pd.DataFrame, **kwargs) -> None:
    try:
        st.dataframe(frame, hide_index=True, width="stretch", **kwargs)
    except TypeError:
        st.dataframe(frame, hide_index=True, use_container_width=True, **kwargs)


def light_mode() -> bool:
    return bool(st.session_state.get("fl_light_mode", False))


def ink() -> str:
    """Primary chart ink for the active theme (use for traces drawn in the text colour)."""
    return "#172b3b" if light_mode() else INK


def style(fig: go.Figure, height: int = 340) -> go.Figure:
    light = light_mode()
    INK, MUTED, LINE = ("#172b3b", "#526b7e", "#d3dfe6") if light else (globals()["INK"], globals()["MUTED"], globals()["LINE"])
    fig.update_layout(
        height=height, margin=dict(l=76, r=44, t=72, b=86), paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,.85)" if light else "rgba(9,22,37,.72)", font=dict(family="Inter, Segoe UI, system-ui, sans-serif", color=INK, size=13),
        hoverlabel=dict(bgcolor="#ffffff" if light else "#102239", bordercolor=LINE, font=dict(color=INK, size=12)),
        legend=dict(orientation="h", y=-0.24, yanchor="top", x=0),
    )
    fig.update_xaxes(gridcolor=LINE, zeroline=False, automargin=True, title_standoff=14, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=LINE, zeroline=False, automargin=True, title_standoff=14, tickfont=dict(color=MUTED))
    return fig


# ---- shared state ---------------------------------------------------------------
@dataclass(frozen=True)
class Settings:
    model: str
    excluded: tuple[str, ...]


def sidebar() -> Settings:
    """Same widgets, same keys on every page, so choices persist while navigating."""
    with st.sidebar:
        with st.expander("Global model controls", expanded=False):
            model = st.radio(
                "Model used in this review", MODEL_NAMES, key="model_name",
                help="Compare models on Model performance. Keep the final test set for a deliberate final review.",
            )
            st.caption("INPUTS THE MODEL MAY USE")
            use_age = st.checkbox("Age", value=True, key="use_age")
            use_status = st.checkbox("Personal status and sex", value=True, key="use_status")
            st.caption(
                "Removing an input does not remove information carried by related features. Check whether the group gap moves."
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


def demo_active() -> bool:
    return bool(st.session_state.get("use_demo_data")) and not dataset_path().exists()


@st.cache_data(show_spinner=False)
def _demo() -> pd.DataFrame:
    return make_demo_dataset()


def demo_banner() -> None:
    st.markdown(
        '<span class="fl-chip demo">SYNTHETIC DEMO DATA</span> <span style="color:var(--fl-amber);font-size:.85rem">'
        "Invented records with the German Credit layout, for exploring the tools offline. Not real evidence; "
        "download the real benchmark on the data page for genuine results.</span>",
        unsafe_allow_html=True,
    )


def require_data() -> pd.DataFrame:
    """Return the validated dataset (or the clearly-labelled synthetic demo), or explain how to get it and stop."""
    path = dataset_path()
    if demo_active():
        demo_banner()
        return _demo()
    if not path.exists():
        callout(
            "The dataset is not on this computer yet",
            "FairLens never downloads data on its own. Select the button to fetch the UCI German Credit "
            "file once; it is saved to <code>data/raw/</code> and kept out of Git. No internet? "
            "Explore every tool right now with a clearly-labelled <b>synthetic</b> demo dataset.",
            "caution",
        )
        c1, c2 = st.columns(2)
        if c1.button("Download the dataset from UCI", type="primary"):
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
        if c2.button("Explore with synthetic demo data"):
            st.session_state["use_demo_data"] = True
            st.rerun()
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
    key = -1.0 if demo_active() else dataset_path().stat().st_mtime
    return _audit(data, settings.excluded, RANDOM_STATE, key)


def provenance_note(data: pd.DataFrame) -> None:
    if demo_active():
        return demo_banner()
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
                    # Exact rates and intervals are available on hover. Leaving
                    # labels out of the plot prevents the three narrow panels
                    # from colliding when group rates are close together.
                    x=[rate], y=[f"{g} (n={int(r[den_col])})"], mode="markers",
                    marker=dict(size=13, color=GROUP_COLOR.get(g, SAGE), symbol="diamond" if g == YOUNG else "circle"),
                    error_x=dict(type="data", symmetric=False, array=[hi - rate], arrayminus=[rate - lo],
                                 color=GROUP_COLOR.get(g, SAGE), thickness=2),
                    showlegend=False,
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
            text=text, texttemplate="%{text}", textfont=dict(color=ink(), size=13),
            colorscale=[[0, "#e4edf2"], [1, "#9fdccb"]] if light_mode() else [[0, "#102239"], [1, "#185a56"]], showscale=False,
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
    max_cost = float(table["cost_per_applicant"].max())
    fig.update_xaxes(title="Average cost per applicant (lower is better)", range=[0, max(max_cost * 1.22, 1.0)])
    return style(fig, 260)


def sweep_chart(sweep: pd.DataFrame, marks: dict[str, float]) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.12,
        subplot_titles=("Average cost per applicant (all applicants)", "Share classified Good, by age group"),
    )
    allrows = sweep[sweep["group"] == "All"]
    fig.add_trace(go.Scatter(x=allrows["threshold"], y=allrows["cost_per_applicant"], mode="lines",
                             line=dict(color=ink(), width=2.5), name="Cost", showlegend=False), row=1, col=1)
    for g in (OLD, YOUNG):
        part = sweep[sweep["group"] == g]
        fig.add_trace(go.Scatter(x=part["threshold"], y=part["predicted_good_rate"], mode="lines",
                                 line=dict(color=GROUP_COLOR[g], width=2.5, dash="dash" if g == YOUNG else "solid"), name=g),
                      row=2, col=1)
    styles = {"Your setting": (GREEN, "solid"), "Best on validation": (AMBER, "dot"), "Theory (5/6)": (MUTED, "dot")}
    for i, (label, x) in enumerate(marks.items()):
        color, dash = styles.get(label, (MUTED, "dot"))
        for r in (1, 2):
            fig.add_vline(x=x, line=dict(color=color, dash=dash, width=1.5), row=r, col=1)
        fig.add_annotation(
            x=x, y=1.0, yref="paper", yshift=8 + i * 17, text=label,
            showarrow=False, font=dict(color=color, size=11), yanchor="bottom",
        )
    fig.update_xaxes(title="Decision threshold: classify Good when P(Good) is at least this", row=2, col=1)
    fig.update_yaxes(tickformat=".0%", row=2, col=1)
    style(fig, 520)
    fig.update_layout(margin=dict(l=84, r=44, t=110, b=94))
    return fig


def stability_chart(runs: dict[str, pd.DataFrame]) -> go.Figure:
    fig = go.Figure()
    for i, (name, frame) in enumerate(runs.items()):
        fig.add_trace(go.Box(x=frame["predicted_good_gap"], name=name, boxpoints="all", jitter=0.5, pointpos=0,
                             marker=dict(color=[GREEN, AMBER][i % 2], size=6, opacity=.75), line=dict(color=ink())))
    fig.add_vline(x=0, line=dict(color=MUTED, dash="dot"))
    fig.update_xaxes(title="Under 25 minus 25 or older: share classified Good (percentage points)", tickformat=".0%")
    return style(fig, 300)


# ---- shared widgets for the hands-on tools ------------------------------------------------------
def score_bar(p: float, threshold: float) -> None:
    """Horizontal scale from 0 to 1: the solid marker is the model's score, the dashed line the threshold."""
    st.markdown(
        f'<div class="fl-bar"><i style="left:calc({p * 100:.1f}% - 2px)"></i><u style="left:{threshold * 100:.1f}%"></u>'
        f'<span style="left:{p * 100:.1f}%;top:-22px;font-weight:600;color:{ink()}">score {p:.2f}</span>'
        f'<span style="left:{threshold * 100:.1f}%">threshold {threshold:.2f}</span></div>',
        unsafe_allow_html=True,
    )


def decision_chip(p: float, threshold: float) -> str:
    good = p >= threshold
    return f'<span class="fl-chip {"good" if good else "bad"}">Model classification: {"Good" if good else "Bad"} risk</span>'


def contribution_chart(table: pd.DataFrame, top: int = 8, height: int = 330) -> go.Figure:
    t = table.head(top).iloc[::-1]
    extent = float(t["contribution"].abs().max()) if not t.empty else 0.1
    fig = go.Figure(go.Bar(
        x=t["contribution"], y=[f"{f}: {v}" for f, v in zip(t["feature"], t["value"])], orientation="h",
        marker_color=[GREEN if c >= 0 else AMBER for c in t["contribution"]],
        text=[f"{c:+.2f}" for c in t["contribution"]], textposition="outside",
        hovertemplate="%{y}<br>moves the score by %{x:+.3f}<extra></extra>",
    ))
    fig.update_xaxes(
        title={"text": "← pushes toward Bad<br>Pushes toward Good →", "standoff": 12},
        range=[-max(extent * 1.35, .1), max(extent * 1.35, .1)],
    )
    fig = style(fig, height)
    # Give the two-line direction label its own centered space below the ticks.
    fig.update_layout(margin=dict(l=76, r=44, t=72, b=112))
    return fig


def card(title: str, body: str, eyebrow: str | None = None) -> None:
    mark = f'<div class="fl-card-id">{eyebrow}</div>' if eyebrow else ""
    st.markdown(f'<div class="fl-card">{mark}<h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)


def friendly_profile(row: pd.DataFrame) -> pd.DataFrame:
    from fairlens.config import feature_label, value_label
    r = row.iloc[0]
    return pd.DataFrame({"Input": [feature_label(c) for c in row.columns], "Value": [value_label(c, r[c]) for c in row.columns]})

