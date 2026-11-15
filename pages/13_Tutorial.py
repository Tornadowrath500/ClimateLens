from __future__ import annotations

import streamlit as st

from fairlens.ui import setup_page


setup_page("Your first FairLens tour")

st.markdown(
    """
    <style>
    .fl-tour-scene { position:relative; min-height:285px; overflow:hidden; display:grid; place-items:center;
      margin:1rem 0 1.25rem; border:1px solid rgba(97,201,255,.25); border-radius:20px;
      background:radial-gradient(ellipse at 50% 40%,rgba(30,93,111,.45),transparent 54%),linear-gradient(145deg,#0b1b2c,#091525); }
    .fl-tour-scene::before { content:""; position:absolute; inset:0; opacity:.28; background-image:
      linear-gradient(rgba(97,201,255,.14) 1px,transparent 1px),linear-gradient(90deg,rgba(97,201,255,.14) 1px,transparent 1px);
      background-size:28px 28px; mask-image:radial-gradient(ellipse at center,#000,transparent 78%); }
    .fl-tour-orbit { position:absolute; width:220px; height:220px; border:1px solid rgba(97,201,255,.22); border-radius:50%; animation:fl-orbit 18s linear infinite; }
    .fl-tour-orbit::before,.fl-tour-orbit::after { content:""; position:absolute; width:8px; height:8px; border-radius:50%; background:#61c9ff; box-shadow:0 0 16px #61c9ff; }
    .fl-tour-orbit::before { top:25px; left:33px; } .fl-tour-orbit::after { bottom:31px; right:26px; background:#f2b84b; box-shadow:0 0 16px #f2b84b; }
    .fl-tour-card { position:relative; z-index:1; width:min(480px,80%); padding:1.25rem 1.35rem; border:1px solid rgba(97,201,255,.32);
      border-radius:16px; background:linear-gradient(145deg,rgba(16,36,58,.96),rgba(9,24,40,.96));
      box-shadow:0 20px 60px rgba(0,0,0,.28),0 0 42px rgba(66,221,179,.09); animation:fl-card-in .65s cubic-bezier(.2,.8,.2,1) both; }
    .fl-tour-tag { color:#61c9ff; font:700 .66rem/1.4 ui-monospace,Consolas,monospace; letter-spacing:.15em; }
    .fl-tour-title { margin:.45rem 0 1rem; color:#e6f1ff; font:650 1.15rem/1.25 Inter,"Segoe UI",sans-serif; }
    .fl-tour-row { display:flex; align-items:center; gap:.8rem; margin:.7rem 0; color:#bdcad7; font:500 .82rem/1.4 Inter,"Segoe UI",sans-serif; }
    .fl-tour-dot { width:10px; height:10px; border-radius:50%; background:#42ddb3; box-shadow:0 0 16px rgba(66,221,179,.8); animation:fl-dot 1.8s ease-in-out infinite; }
    .fl-tour-bar { flex:1; height:9px; overflow:hidden; border-radius:99px; background:#20384d; }
    .fl-tour-bar i { display:block; height:100%; border-radius:inherit; transform-origin:left; background:linear-gradient(90deg,#61c9ff,#42ddb3); animation:fl-bar-grow 1.15s cubic-bezier(.2,.8,.2,1) both; }
    .fl-tour-nodes { display:flex; align-items:center; justify-content:space-between; gap:.5rem; }
    .fl-tour-node { display:grid; flex:1; min-width:0; place-items:center; width:74px; height:74px; padding:.4rem; border:1px solid rgba(97,201,255,.3); border-radius:18px; color:#e6f1ff; text-align:center; font:650 .7rem/1.3 Inter,"Segoe UI",sans-serif; background:#10263a; animation:fl-node-float 3.2s ease-in-out infinite; }
    .fl-tour-node:nth-child(2) { animation-delay:.35s; border-color:rgba(66,221,179,.4); }
    .fl-tour-node:nth-child(3) { animation-delay:.7s; border-color:rgba(242,184,75,.4); }
    .fl-tour-arrow { color:#42ddb3; font-size:1.2rem; animation:fl-arrow 1.5s ease-in-out infinite; }
    .fl-tour-sliders { display:grid; gap:1rem; margin:.6rem 0; }
    .fl-tour-track { position:relative; height:8px; border-radius:99px; background:#20384d; }
    .fl-tour-track::before { content:""; display:block; height:100%; width:var(--fill); border-radius:inherit; background:linear-gradient(90deg,#61c9ff,#42ddb3); }
    .fl-tour-knob { position:absolute; top:50%; left:var(--fill); width:19px; height:19px; border:3px solid #e6f1ff; border-radius:50%; background:#42ddb3; box-shadow:0 0 18px rgba(66,221,179,.8); transform:translate(-50%,-50%); animation:fl-knob 2.4s ease-in-out infinite alternate; }
    .fl-tour-check { display:flex; gap:.8rem; align-items:center; margin:.6rem 0; color:#c6d5e1; font:500 .82rem/1.4 Inter,"Segoe UI",sans-serif; }
    .fl-tour-check b { display:grid; place-items:center; width:23px; height:23px; border-radius:50%; color:#07111f; background:#42ddb3; animation:fl-check-in .4s both; }
    .fl-tour-check:nth-child(3) b { animation-delay:.22s; } .fl-tour-check:nth-child(4) b { animation-delay:.44s; }
    @keyframes fl-orbit { to { transform:rotate(360deg); } }
    @keyframes fl-card-in { from { opacity:0; transform:translateY(18px) scale(.97); } to { opacity:1; transform:translateY(0) scale(1); } }
    @keyframes fl-dot { 50% { transform:scale(1.45); box-shadow:0 0 22px rgba(66,221,179,1); } }
    @keyframes fl-bar-grow { from { transform:scaleX(0); } to { transform:scaleX(1); } }
    @keyframes fl-node-float { 50% { transform:translateY(-7px); } }
    @keyframes fl-arrow { 50% { transform:translateX(4px); opacity:.65; } }
    @keyframes fl-knob { to { left:calc(var(--fill) - 9%); } }
    @keyframes fl-check-in { from { opacity:0; transform:scale(.4) rotate(-25deg); } to { opacity:1; transform:scale(1) rotate(0); } }
    @media (prefers-reduced-motion:reduce) { .fl-tour-scene *, .fl-tour-scene *::before, .fl-tour-scene *::after { animation:none !important; scroll-behavior:auto !important; } }
    @media (max-width:520px) { .fl-tour-scene { min-height:250px; } .fl-tour-card { width:90%; padding:.85rem; } .fl-tour-node { width:58px; height:62px; font-size:.6rem; } .fl-tour-nodes { gap:.35rem; } }
    </style>
    """,
    unsafe_allow_html=True,
)

steps = [
    {
        "tag": "01 / GET ORIENTED",
        "title": "Start with the evidence",
        "body": "FairLens uses a historic credit-risk benchmark. Begin with its labels, feature definitions, source, and known limits before interpreting any chart.",
        "page": "pages/1_Understand_the_Data.py",
        "link": "Explore the data and its scope",
        "scene": """<div class="fl-tour-card"><div class="fl-tour-tag">DATA / SOURCE / LIMITS</div><div class="fl-tour-title">Know what went into the model</div><div class="fl-tour-row"><span class="fl-tour-dot"></span><span>1,000 historical records</span><span class="fl-tour-bar"><i style="width:82%"></i></span></div><div class="fl-tour-row"><span class="fl-tour-dot" style="background:#f2b84b"></span><span>20 input features</span><span class="fl-tour-bar"><i style="width:64%;background:linear-gradient(90deg,#f2b84b,#61c9ff)"></i></span></div></div>""",
    },
    {
        "tag": "02 / INSPECT THE MODEL",
        "title": "See how it performs",
        "body": "Compare a simple baseline with candidate models. Read the types of mistakes and their costs alongside accuracy; one summary number never tells the whole story.",
        "page": "pages/2_Evaluate_the_Model.py",
        "link": "Compare model performance",
        "scene": """<div class="fl-tour-card"><div class="fl-tour-tag">FEATURES → MODEL → OUTPUT</div><div class="fl-tour-title">A score is a starting point</div><div class="fl-tour-nodes"><div class="fl-tour-node">Applicant<br>features</div><span class="fl-tour-arrow">›</span><div class="fl-tour-node">Risk<br>model</div><span class="fl-tour-arrow">›</span><div class="fl-tour-node">Score +<br>decision</div></div></div>""",
    },
    {
        "tag": "03 / CHECK GROUP OUTCOMES",
        "title": "Look for gaps, then investigate",
        "body": "Compare outcome rates across the app’s age groups. Keep denominators and uncertainty in view: a measured difference is a reason to ask questions, not proof of cause.",
        "page": "pages/3_Investigate_Group_Outcomes.py",
        "link": "Explore group outcomes",
        "scene": """<div class="fl-tour-card"><div class="fl-tour-tag">GROUP OUTCOMES / WITH CONTEXT</div><div class="fl-tour-title">Compare rates with their sample sizes</div><div class="fl-tour-row"><span>Under 25</span><span class="fl-tour-bar"><i style="width:43%"></i></span><span>n shown</span></div><div class="fl-tour-row"><span>25 and over</span><span class="fl-tour-bar"><i style="width:69%;background:linear-gradient(90deg,#f2b84b,#42ddb3)"></i></span><span>n shown</span></div></div>""",
    },
    {
        "tag": "04 / TRY A WHAT-IF",
        "title": "Explore trade-offs safely",
        "body": "Use fictional profiles and validation-only experiments to see how thresholds or inputs change results. A what-if is a learning tool, not a recommended decision rule.",
        "page": "pages/4_Experiment_Lab.py",
        "link": "Open the experiment lab",
        "scene": """<div class="fl-tour-card"><div class="fl-tour-tag">WHAT-IF / VALIDATION ONLY</div><div class="fl-tour-title">Move a threshold. Watch the trade-off.</div><div class="fl-tour-sliders"><div class="fl-tour-track" style="--fill:44%"><span class="fl-tour-knob"></span></div><div class="fl-tour-track" style="--fill:72%"><span class="fl-tour-knob"></span></div><div class="fl-tour-track" style="--fill:59%"><span class="fl-tour-knob"></span></div></div><div class="fl-tour-row"><span class="fl-tour-dot"></span><span>Errors, costs, and group rates update together</span></div></div>""",
    },
    {
        "tag": "05 / SHARE A CLEAR REVIEW",
        "title": "Finish with a reproducible summary",
        "body": "Bring the selected model, evaluation split, measured findings, and limitations together. FairLens keeps uncertainty and context visible in its report.",
        "page": "pages/5_Findings_and_Report.py",
        "link": "See findings and reporting",
        "scene": """<div class="fl-tour-card"><div class="fl-tour-tag">FINDINGS / METHODS / LIMITS</div><div class="fl-tour-title">A careful review has receipts</div><div class="fl-tour-check"><b>✓</b><span>Metrics and denominators</span></div><div class="fl-tour-check"><b>✓</b><span>Model and split recorded</span></div><div class="fl-tour-check"><b>✓</b><span>Uncertainty and limitations</span></div></div>""",
    },
]

if "fl_tutorial_step" not in st.session_state:
    st.session_state["fl_tutorial_step"] = 0
index = max(0, min(st.session_state["fl_tutorial_step"], len(steps) - 1))
step = steps[index]

st.markdown('<div class="fl-eyebrow">FAIRLENS / A 90-SECOND FIELD GUIDE</div>', unsafe_allow_html=True)
st.title("Your first FairLens tour")
st.markdown('<p class="fl-lede">Five quick stops. A moving picture of the workflow. You can replay this tour any time.</p>', unsafe_allow_html=True)
st.progress((index + 1) / len(steps))
st.caption(f"STEP {index + 1:02d} / {len(steps):02d}  ·  {step['tag']}")

st.markdown(f'<div class="fl-tour-scene">{step["scene"]}<div class="fl-tour-orbit"></div></div>', unsafe_allow_html=True)
st.markdown(f"### {step['title']}")
st.write(step["body"])
st.page_link(step["page"], label=step["link"], icon=":material/arrow_outward:")

previous, replay, next_step = st.columns([1, 1, 1])
with previous:
    if st.button("← Back", disabled=index == 0, use_container_width=True):
        st.session_state["fl_tutorial_step"] = index - 1
        st.rerun()
with replay:
    if st.button("↺ Start over", use_container_width=True):
        st.session_state["fl_tutorial_step"] = 0
        st.session_state["fl_tutorial_done"] = False
        st.rerun()
with next_step:
    label = "Finish tour ✓" if index == len(steps) - 1 else "Next →"
    if st.button(label, type="primary", use_container_width=True):
        if index == len(steps) - 1:
            st.session_state["fl_tutorial_done"] = True
            st.success("Tour complete. You’re ready to explore FairLens at your own pace.")
            st.page_link("pages/0_Home.py", label="Go to FairLens home", icon=":material/home:")
        else:
            st.session_state["fl_tutorial_step"] = index + 1
            st.rerun()
