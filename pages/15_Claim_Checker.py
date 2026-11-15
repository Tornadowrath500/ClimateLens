from __future__ import annotations

import streamlit as st

from fairlens.ui import callout, card, header, setup_page, sidebar

setup_page("Claim checker")
sidebar()
header(
    "Claim checker",
    "Audits are easy to over-read. Stress-test a claim against the evidence you actually have.",
)

CLAIMS = {
    "The model is fair.": {
        "can": "Compare measured rates and errors for the groups in this dataset, with sample sizes and uncertainty.",
        "cannot": "Prove that the model is fair overall. Fairness has competing definitions and no single metric settles it.",
        "evidence": [
            "I named the fairness definition being examined.",
            "I reported group sizes and uncertainty, not rates alone.",
            "I checked more than one relevant metric.",
            "I understand how labels were produced and their limitations.",
            "I considered who bears the cost of each type of error.",
        ],
        "page": ("pages/3_Investigate_Group_Outcomes.py", "Group outcomes"),
    },
    "The model discriminates against younger applicants.": {
        "can": "Measure whether outcomes differ between the age groups defined in this historical dataset.",
        "cannot": "Establish discrimination, causation, or a legal conclusion from a rate gap alone.",
        "evidence": [
            "I measured the gap with denominators and uncertainty.",
            "I checked whether related inputs can proxy for age.",
            "I compared similar records as well as group averages.",
            "I have evidence about how the real decision process used the model.",
            "A qualified domain or legal expert reviewed the claim.",
        ],
        "page": ("pages/9_Proxy_Detector.py", "Proxy detector"),
    },
    "Removing age makes the model fair.": {
        "can": "Show how measured outcomes change when age is omitted from this model.",
        "cannot": "Show that related inputs no longer carry age-related information or that the model is fair.",
        "evidence": [
            "I compared both models using the same evaluation split.",
            "I checked remaining inputs for proxy information.",
            "I reported uncertainty around group differences.",
            "I checked the effect on overall errors and their costs.",
        ],
        "page": ("pages/10_Mitigation_Lab.py", "Mitigation lab"),
    },
    "These results describe applicants today.": {
        "can": "Describe a simple model's behavior on a small historical German credit benchmark.",
        "cannot": "Describe current applicants, lenders, other places, or later periods.",
        "evidence": [
            "I have recent data from the setting of interest.",
            "I verified the data collection and coding fit that setting.",
            "I validated the analysis locally with appropriate oversight.",
        ],
        "page": ("pages/1_Understand_the_Data.py", "Data & scope"),
    },
    "The health simulation shows real screening is biased.": {
        "can": "Illustrate how threshold and score assumptions can change error rates in invented records.",
        "cannot": "Establish anything about actual patients, screening tools, or health systems.",
        "evidence": [
            "I have appropriately governed data for the intended setting.",
            "Clinical and community experts reviewed labels and outcomes.",
            "The analysis was independently validated for local use.",
        ],
        "page": ("pages/14_Health_Equity_Lab.py", "Health equity lab"),
    },
}

claim = st.selectbox("Choose a claim to stress-test", list(CLAIMS), help="These examples are not claims about a specific system.")
item = CLAIMS[claim]
left, right = st.columns(2, gap="medium")
with left:
    card("What the evidence can support", item["can"], eyebrow="SUPPORTED")
with right:
    card("What it cannot establish", item["cannot"], eyebrow="LIMITS")

st.subheader("Evidence to check before repeating this claim")
checks = [st.checkbox(text, key=f"claim::{claim}::{i}") for i, text in enumerate(item["evidence"])]
have, total = sum(checks), len(checks)
if have == total:
    note = "Every item is checked. The claim still depends on data quality and expert review."
elif not have:
    note = "No supporting evidence checked yet. Treat the claim as unsubstantiated."
else:
    missing = [text for text, checked in zip(item["evidence"], checks) if not checked]
    note = f"Still missing: {missing[0]}" + (f" (plus {len(missing)-1} more)" if len(missing)>1 else "")
st.progress(have / total, text=f"Evidence checklist: {have} of {total}")
st.caption(note)

review = "\n".join(
    ["FairLens claim review", f"Claim: {claim}", f"Can show: {item['can']}", f"Cannot establish: {item['cannot']}",
     f"Evidence checked: {have} of {total}", ""]
    + [f"[{'x' if checked else ' '}] {text}" for text, checked in zip(item["evidence"], checks)]
    + ["", "Educational reasoning aid only; not legal, financial, or medical advice."]
)
st.download_button("Download claim review", review, file_name="fairlens_claim_review.txt", mime="text/plain")
st.page_link(item["page"][0], label=f"Review related evidence: {item['page'][1]}")

callout(
    "How to read the checklist",
    "This is a reasoning aid, not a pass/fail test. Checking every box does not make a claim true.",
    "caution",
)
