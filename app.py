from __future__ import annotations

import streamlit as st
from fairlens.ui import theme_control


st.set_page_config(
    page_title="FairLens · Model audit",
    page_icon="assets/fairlens-mark.svg",
    layout="wide",
    initial_sidebar_state="auto",
)

theme_control()

navigation = st.navigation(
    {
        "START": [
            st.Page("pages/0_Home.py", title="Home", icon=":material/home:", default=True),
            st.Page("pages/13_Tutorial.py", title="Take the tour", icon=":material/explore:"),
            st.Page("pages/12_Profile.py", title="Session profile (optional)", icon=":material/account_circle:"),
        ],
        "REVIEW THE MODEL": [
            st.Page("pages/1_Understand_the_Data.py", title="Data & scope", icon=":material/database:"),
            st.Page("pages/2_Evaluate_the_Model.py", title="Model performance", icon=":material/monitoring:"),
            st.Page("pages/3_Investigate_Group_Outcomes.py", title="Group outcomes", icon=":material/groups:"),
            st.Page("pages/5_Findings_and_Report.py", title="Findings & report", icon=":material/description:"),
            st.Page("pages/15_Claim_Checker.py", title="Claim checker", icon=":material/rule:"),
            st.Page("pages/6_Methodology_and_Limitations.py", title="Methods & limits", icon=":material/menu_book:"),
        ],
        "TRY IT": [
            st.Page("pages/14_Hidden_Bias_Challenge.py", title="Hidden bias challenge", icon=":material/quiz:"),
            st.Page("pages/17_Overclaim_Game.py", title="Over-claim game", icon=":material/sports_esports:"),
        ],
        "EXPLORE & TEST": [
            st.Page("pages/7_Applicant_Map.py", title="Applicant map", icon=":material/map:"),
            st.Page("pages/8_Applicant_Simulator.py", title="Applicant simulator", icon=":material/tune:"),
            st.Page("pages/9_Proxy_Detector.py", title="Proxy detector", icon=":material/radar:"),
            st.Page("pages/4_Experiment_Lab.py", title="Experiment lab", icon=":material/experiment:"),
            st.Page("pages/10_Mitigation_Lab.py", title="Mitigation lab", icon=":material/compare_arrows:"),
            st.Page("pages/11_Audit_Your_Model.py", title="Audit your model", icon=":material/fact_check:"),
            st.Page("pages/14_Health_Equity_Lab.py", title="Health lab (synthetic)", icon=":material/health_metrics:"),
        ],
    },
    position="sidebar",
    expanded=True,
)

navigation.run()

