from __future__ import annotations

import streamlit as st

from fairlens.config import dataset_path
from fairlens.data import load_dataset
from fairlens.models import MODEL_NAMES
from fairlens.ui import Settings, card, demo_active, demo_banner, get_audit, get_op, require_data, setup_page


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
cta1, cta2, cta3 = st.columns(3, gap="small")
cta1.page_link("pages/13_Tutorial.py", label="Take the 3-minute tour", icon=":material/explore:")
cta2.page_link("pages/1_Understand_the_Data.py", label="Start the audit", icon=":material/play_arrow:")
cta3.page_link("pages/5_Findings_and_Report.py", label="Jump to the findings", icon=":material/description:")

if dataset_path().exists() and not demo_active():
    snapshot = load_dataset()
    records, features, source_label = f"{len(snapshot):,}", str(snapshot.shape[1] - 1), "UCI benchmark, 1994"
elif demo_active():
    records, features, source_label = "1,000", "20", "Synthetic demo"
else:
    records, features, source_label = "Not loaded", "20", "Not loaded yet"
st.markdown(
    '<div class="fl-stats">'
    f'<div class="fl-stat"><b>{records}</b><span>records in view</span></div>'
    f'<div class="fl-stat"><b>{features}</b><span>input features per record</span></div>'
    '<div class="fl-stat"><b>5 : 1</b><span>cost of calling a Bad case Good versus the reverse</span></div>'
    f'<div class="fl-stat"><b class="fl-stat-text">{source_label}</b><span>evidence source: not today\'s lending</span></div>'
    '</div>',
    unsafe_allow_html=True,
)

have_data = dataset_path().exists() or demo_active()
if not have_data:
    st.info("The benchmark is not loaded on this computer yet. Start with the data page, or explore the interface using clearly labelled synthetic demo data.")
    if st.button("Explore with synthetic demo data", type="primary", icon=":material/auto_awesome:"):
        st.session_state["use_demo_data"] = True
        st.rerun()
elif demo_active():
    demo_banner()

st.markdown('<div class="fl-section-kicker">FAIRLENS IN 30 SECONDS</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3, gap="medium")
with c1:
    card("What it does", "Trains a simple credit-risk model on a public 1994 dataset, then shows where it is right, where it errs, and how errors differ between groups.", eyebrow="DOES")
with c2:
    card("What results mean", "A gap between groups is a prompt to ask why: data coding, group size, thresholds, or related inputs. It is not a verdict.", eyebrow="MEANS")
with c3:
    card("What it cannot prove", "Discrimination, causes, or how any real lender or health system behaves today. Small groups carry wide uncertainty.", eyebrow="CANNOT")
st.markdown(
    '<span class="fl-chip">HISTORICAL · German Credit, 1,000 records</span> '
    '<span class="fl-chip demo">SYNTHETIC · Health lab and demo data</span> '
    '<span class="fl-chip">YOUR DATA · Audit your model (stays in this session)</span>',
    unsafe_allow_html=True,
)
_terms = {
    "Threshold": "The score cut-off. Scores at or above it are classified Good.",
    "Bad case classified Good": "The costlier mistake here: cost 5, versus 1 for the reverse.",
    "95% interval": "A plausible range for a rate given the sample size. Wide means little data.",
    "Proxy": "An input that indirectly carries a sensitive trait such as age.",
    "Mitigation": "A change meant to narrow a gap. It usually trades off against accuracy or cost.",
    "Sensitivity": "The share of actual positive cases that a screen flags.",
}
st.markdown(
    '<div class="fl-terms"><span class="fl-terms-label">Hover or focus a term</span>'
    + "".join(f'<span class="fl-term" tabindex="0" data-tip="{tip}">{name}</span>' for name, tip in _terms.items())
    + "</div>",
    unsafe_allow_html=True,
)

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

st.markdown('<div class="fl-section-kicker">PICK YOUR PATH</div>', unsafe_allow_html=True)
p1, p2, p3 = st.columns(3, gap="medium")
with p1:
    card("I have 2 minutes", "Take the guided tour, then read the findings summary.", eyebrow="QUICK")
    st.page_link("pages/13_Tutorial.py", label="Start the tour", icon=":material/explore:")
with p2:
    card("I want to test trade-offs", "Move a threshold and watch cost and group gaps change together.", eyebrow="HANDS-ON")
    st.page_link("pages/10_Mitigation_Lab.py", label="Open the mitigation lab", icon=":material/compare_arrows:")
with p3:
    card("I have my own model", "Upload decisions and a group column for rates with intervals.", eyebrow="YOUR DATA")
    st.page_link("pages/11_Audit_Your_Model.py", label="Audit your model", icon=":material/fact_check:")

st.markdown('<div class="fl-section-kicker">SEE IT IN ACTION</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.markdown("**Live headline from the audit**")
    st.caption("Trains the model on the training split (a few seconds the first time), then reads the validation results. Nothing is stored.")
    if st.button("Run the audit and show a headline", icon=":material/bolt:", key="home_headline"):
        st.session_state["home_headline_on"] = True
    if st.session_state.get("home_headline_on") and not have_data:
        st.info("Load the benchmark on the data page, or use the synthetic demo, to run the audit.")
    elif st.session_state.get("home_headline_on"):
        from fairlens.report import compute_group_review
        _data = require_data()
        _settings = Settings(model=MODEL_NAMES[0], excluded=())
        _op = get_op()
        _review = compute_group_review(get_audit(_data, _settings), _settings.model, _op, part="validation")
        for _line in _review["group_observations"][:3]:
            st.markdown(f"- {_line}")
        st.caption(f"{_settings.model}, validation split, {_op.describe()}. A difference is a signal to investigate, not proof of discrimination or its cause.")
        st.page_link("pages/3_Investigate_Group_Outcomes.py", label="See the uncertainty behind these numbers", icon=":material/arrow_outward:")

st.markdown('<div class="fl-section-kicker">TRY IT · WHY ONE MISTAKE COSTS MORE</div>', unsafe_allow_html=True)
with st.container(border=True):
    st.caption("Not every error is equal. Set how many of each mistake a model makes and how much worse the first one is. The benchmark's documentation uses 5 to 1.")
    k1, k2, k3 = st.columns(3, gap="medium")
    n_risky = k1.slider("Bad cases classified Good", 0, 100, 10, key="cx_risky", help="Applicants labelled Bad whom the model classified Good.")
    n_over = k2.slider("Good cases classified Bad", 0, 100, 40, key="cx_over", help="Applicants labelled Good whom the model classified Bad.")
    weight = k3.select_slider("First mistake costs this many times more", options=[1, 2, 3, 5, 8, 10], value=5, key="cx_weight")
    cost_risky, cost_over = n_risky * weight, n_over
    total_cost = cost_risky + cost_over
    share = cost_risky / total_cost if total_cost else 0.0
    st.markdown(
        f'<div class="fl-costbar" role="img" aria-label="Share of total cost: {share:.0%} from Bad cases classified Good">'
        f'<i class="a" style="width:{share * 100:.1f}%"></i><i class="b" style="width:{(1 - share) * 100 if total_cost else 0:.1f}%"></i></div>'
        f'<div class="fl-costkey"><span><b class="a"></b>Bad classified Good: {n_risky} × {weight} = {cost_risky}</span>'
        f'<span><b class="b"></b>Good classified Bad: {n_over} × 1 = {cost_over}</span></div>',
        unsafe_allow_html=True,
    )
    if not total_cost:
        st.caption("No mistakes, no cost. Move a slider to see how the mix changes.")
    elif n_risky < n_over and cost_risky > cost_over:
        st.markdown(f"The rarer mistake drives **{share:.0%}** of the total cost. Counting errors alone would hide that, which is why FairLens reports cost beside accuracy.")
    else:
        st.markdown(f"The costlier mistake accounts for **{share:.0%}** of the total cost. Raise the weight or change the counts to see when it dominates.")

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

