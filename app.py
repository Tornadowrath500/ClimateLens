from __future__ import annotations

import streamlit as st


pages = {
    "Start here": [
        st.Page("pages/0_Overview.py", title="Overview", icon="🏠", default=True),
        st.Page("pages/1_Understand_the_Data.py", title="Understand the data", icon="📋"),
    ],
    "Review the model": [
        st.Page("pages/2_Evaluate_the_Model.py", title="Evaluate performance", icon="📊"),
        st.Page("pages/3_Investigate_Group_Outcomes.py", title="Compare group outcomes", icon="⚖️"),
        st.Page("pages/4_Experiment_Lab.py", title="Test decision changes", icon="🧪"),
        st.Page("pages/5_Findings_and_Report.py", title="Findings and report", icon="📝"),
        st.Page("pages/6_Methodology_and_Limitations.py", title="Methods and limits", icon="ℹ️"),
    ],
    "Explore applicants": [
        st.Page("pages/7_Applicant_Map.py", title="Applicant map", icon="🗺️"),
        st.Page("pages/8_Applicant_Simulator.py", title="Applicant simulator", icon="🎛️"),
        st.Page("pages/9_Proxy_Detector.py", title="Proxy detector", icon="🔎"),
    ],
    "Audit and improve": [
        st.Page("pages/10_Mitigation_Lab.py", title="Mitigation lab", icon="🧭"),
        st.Page("pages/11_Audit_Your_Model.py", title="Audit your own model", icon="📥"),
    ],
}

navigation = st.navigation(pages, position="sidebar", expanded=True)
navigation.run()
