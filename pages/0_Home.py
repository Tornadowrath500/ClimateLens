from __future__ import annotations

import streamlit as st

from fairlens.config import dataset_path, TARGET_COLUMN
from fairlens.data import load_dataset
from fairlens.ui import callout, card, demo_active, demo_banner, header, setup_page


setup_page("Home")

st.markdown(
    '<section class="fl-hero">'
    '<div class="fl-eyebrow"><span class="fl-pulse"></span> MODEL AUDIT / HUMAN IMPACT</div>'
    '<h1>Make model decisions visible.</h1>'
    '<p>Explore a historic credit-risk model, compare its mistakes across groups, and see what changes when its inputs or decision rules change.</p>'
    '<div class="fl-hero-meta"><span>01 · DATA</span><span>02 · OUTCOMES</span><span>03 · TRADE-OFFS</span></div>'
    '</section>',
    unsafe_allow_html=True,
)

if dataset_path().exists() and not demo_active():
    snapshot = load_dataset()
    records = len(snapshot)
    features = snapshot.shape[1] - 1
    source_label = "Historic UCI benchmark"
elif demo_active():
    records, features, source_label = 1000, 20, "Synthetic demo"
else:
    records, features, source_label = 0, 20, "Dataset not loaded"

st.markdown('<div class="fl-section-kicker">AUDIT WORKSPACE / START HERE</div>', unsafe_allow_html=True)
m1, m2, m3 = st.columns([1, 1, 2], gap="medium")
with m1:
    st.metric("Records in view", f"{records:,}" if records else "Not loaded")
with m2:
    st.metric("Input features", f"{features}")
with m3:
    st.metric("Evidence source", source_label, help="FairLens uses a historic credit benchmark or clearly labeled synthetic examples; it does not sync current applicant data.")
st.markdown(
    '<section class="fl-dashboard-callout"><div><span class="fl-eyebrow">YOUR FIRST 3 MINUTES</span>'
    '<h3>Start with the evidence. Leave with a careful claim.</h3>'
    '<p>Understand the benchmark, inspect model errors, then compare group outcomes before exploring changes.</p></div></section>',
    unsafe_allow_html=True,
)
quick = st.columns(4, gap="small")
for col, path, label, icon in zip(
    quick,
    ["pages/1_Understand_the_Data.py", "pages/2_Evaluate_the_Model.py", "pages/3_Investigate_Group_Outcomes.py", "pages/15_Claim_Checker.py"],
    ["01 · Data", "02 · Performance", "03 · Groups", "04 · Claim check"],
    [":material/database:", ":material/monitoring:", ":material/groups:", ":material/rule:"],
):
    with col:
        st.page_link(path, label=label, icon=icon)

callout(
    "A research and learning tool",
    "The public UCI benchmark is bundled and ready to explore; no data download is needed. FairLens is an educational tool, not designed for real lending decisions. Group differences are a signal to investigate, not proof of discrimination or its cause.",
    "note",
)

if not st.session_state.get("fl_tutorial_done"):
    with st.container(border=True):
        st.markdown("### New to FairLens?")
        st.write("Take the animated, step-by-step tour to see how the data, model, group comparisons, and experiments fit together.")
        st.page_link("pages/13_Tutorial.py", label="Start the animated tour", icon=":material/play_circle:")

profile = st.session_state.get("fl_profile")
if profile and st.session_state.get("fl_profile_active"):
    name = profile.get("display_name")
    avatar = profile.get("avatar", "🔎")
    st.subheader(f"{avatar}  Welcome, {name}." if name else f"{avatar}  Welcome.")
    st.page_link("pages/12_Profile.py", label="Customize your profile", icon=":material/tune:")
    suggestions = []
    if profile.get("age") is not None:
        suggestions.append((
            "Age and group outcomes",
            "See how FairLens defines its under-25 and 25-and-over comparison, and where that split is limited.",
            "pages/3_Investigate_Group_Outcomes.py",
            ":material/groups:",
        ))
    if profile.get("sex") != "Prefer not to say" or profile.get("personal_status") != "Prefer not to say":
        suggestions.append((
            "Sensitive fields in the data",
            "Learn how the historic benchmark combines personal status and sex in one field.",
            "pages/1_Understand_the_Data.py",
            ":material/database:",
        ))
    interest_pages = {
        "Model performance": ("Compare model performance", "Review model errors and their different costs.", "pages/2_Evaluate_the_Model.py", ":material/monitoring:"),
        "Fairness across groups": ("Explore group outcomes", "Compare rates with denominators and uncertainty.", "pages/3_Investigate_Group_Outcomes.py", ":material/groups:"),
        "How predictions work": ("Explore an applicant profile", "Use fictional profiles to inspect scores and what-if changes.", "pages/8_Applicant_Simulator.py", ":material/tune:"),
        "Hands-on experiments": ("Try an experiment", "Explore threshold changes and their trade-offs.", "pages/4_Experiment_Lab.py", ":material/science:"),
    }
    for interest in profile.get("interests", []):
        item = interest_pages[interest]
        if item[2] not in [suggestion[2] for suggestion in suggestions]:
            suggestions.append(item)
    if not suggestions:
        suggestions.append((
            "Start with the data",
            "See what the historical records contain and what they leave out.",
            "pages/1_Understand_the_Data.py",
            ":material/database:",
        ))
    with st.container(border=True):
        st.markdown("**Suggested for you**")
        for title, description, page, icon in suggestions[:3]:
            st.write(description)
            st.page_link(page, label=title, icon=icon)

have_data = dataset_path().exists() or demo_active()
if not have_data:
    st.info("The benchmark is not loaded on this computer yet. Start with the data page, or explore the interface using clearly labelled synthetic demo data.")
    if st.button("Explore with synthetic demo data", type="primary", icon=":material/auto_awesome:"):
        st.session_state["use_demo_data"] = True
        st.rerun()
elif demo_active():
    demo_banner()

st.markdown('<div class="fl-section-kicker">START WITH A QUESTION</div>', unsafe_allow_html=True)
st.subheader("Choose your next move")
destinations = [
    ("01", "Understand the data", "See what the historic records contain and what they leave out.", "pages/1_Understand_the_Data.py", "Open data & scope"),
    ("02", "Inspect model performance", "Compare baselines and model errors, including the higher-cost mistake.", "pages/2_Evaluate_the_Model.py", "Compare models"),
    ("03", "Find group differences", "Review rates with denominators and uncertainty beside every comparison.", "pages/3_Investigate_Group_Outcomes.py", "Group outcomes"),
    ("04", "Explore the applicant map", "Locate clusters of similar profiles and inspect individual model scores.", "pages/7_Applicant_Map.py", "Open the map"),
]
cols = st.columns(4, gap="medium")
for col, (number, title, body, page, label) in zip(cols, destinations):
    with col:
        card(title, body, eyebrow=number)
        st.page_link(page, label=label, icon=":material/arrow_outward:")

st.markdown('<div class="fl-section-kicker">A CAREFUL ROUTE THROUGH THE AUDIT</div>', unsafe_allow_html=True)
steps = [
    ("01", "Data", "Source, labels and limits"),
    ("02", "Model", "Errors and cost"),
    ("03", "People", "Group rates and uncertainty"),
    ("04", "What if?", "Threshold and mitigation trade-offs"),
    ("05", "Findings", "A reproducible review"),
]
flow = "".join(
    f'<div class="fl-flow-step"><span>{number}</span><strong>{title}</strong><small>{body}</small></div>'
    for number, title, body in steps
)
st.markdown(f'<div class="fl-flow">{flow}</div>', unsafe_allow_html=True)

st.markdown('<div class="fl-section-kicker">WIDER CONTEXT</div>', unsafe_allow_html=True)
st.markdown(
    '<section class="fl-health-panel">'
    '<div><span class="fl-health-icon">✳</span></div>'
    '<div><p class="fl-eyebrow">SOCIAL DETERMINANTS / HEALTH CONTEXT</p>'
    '<h3>Model outcomes sit inside people’s lives.</h3>'
    '<p>Public-health research describes economic stability and other social conditions as factors that shape health across populations. That context can motivate careful questions about who carries the cost of model errors.</p>'
    '<p class="fl-limit"><strong>What this app can show:</strong> credit-label outcomes in a small, historic benchmark. <strong>What it cannot show:</strong> health status, access to care, or health effects of a model decision. The benchmark contains no health outcomes, so FairLens makes no individual or causal health claims.</p>'
    '<a href="https://www.who.int/news-room/fact-sheets/detail/social-determinants-of-health" target="_blank" rel="noopener noreferrer">WHO: Social determinants of health ↗</a>'
    '<span class="fl-source-sep">·</span>'
    '<a href="https://www.cdc.gov/about/priorities/why-is-addressing-sdoh-important.html" target="_blank" rel="noopener noreferrer">CDC: Social determinants of health ↗</a>'
    '</div></section>',
    unsafe_allow_html=True,
)

st.caption("Every figure is computed from the selected data and model settings. Synthetic demo records are invented and labelled wherever they appear.")
