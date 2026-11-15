from __future__ import annotations

import numpy as np
import streamlit as st

from fairlens.ui import callout, header, setup_page, sidebar

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

st.subheader("How to use this in a health-sector review")
st.markdown(
    "1. **Start with intended use.** Define the decision, population, setting, and who is affected before choosing metrics.\n"
    "2. **Check label meaning.** A recorded outcome may reflect access, follow-up, or workflow—not only underlying health.\n"
    "3. **Inspect measurement and missingness.** Compare how inputs are collected across groups and sites.\n"
    "4. **Review uncertainty and harms.** Report group counts and uncertainty; discuss both missed cases and unnecessary flags with clinical and community experts.\n"
    "5. **Validate locally before use.** This toy exercise cannot replace clinical validation, privacy review, or monitoring."
)
st.caption("This lab is deterministic for reproducibility. Changing its sliders changes assumptions, not external data. No information is synced from live patient or population sources.")
