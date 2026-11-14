from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="FairLens | Model review",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      :root {
        --fairlens-ink: #223b35;
        --fairlens-green: #315d50;
        --fairlens-muted: #64756e;
        --fairlens-paper: #f6f5f0;
        --fairlens-line: #e4e4dc;
      }
      .stApp { background: var(--fairlens-paper); }
      .block-container { max-width: 1180px; padding-top: 2.2rem; }
      h1, h2, h3 { color: var(--fairlens-ink); letter-spacing: -0.025em; }
      .fairlens-eyebrow {
        color: var(--fairlens-green); font-size: .76rem;
        font-weight: 700; letter-spacing: .12em; text-transform: uppercase;
      }
      .fairlens-subtitle { color: var(--fairlens-muted); font-size: 1.08rem; line-height: 1.6; }
      .fairlens-note {
        border: 1px solid var(--fairlens-line); border-left: 4px solid var(--fairlens-green);
        background: rgba(255,255,255,.65); border-radius: 10px;
        padding: 1rem 1.15rem; color: var(--fairlens-ink);
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="fairlens-eyebrow">A guided model review</div>', unsafe_allow_html=True)
st.title("Understand the decisions behind the model.")
st.markdown(
    '<p class="fairlens-subtitle">FairLens helps you inspect a model, understand how its errors are distributed, '
    "and explore what changes when its decision rules are adjusted.</p>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="fairlens-note">
      <strong>A note on responsible use</strong><br>
      This is an educational analysis of a historical benchmark, not a lending tool or
      financial advice. Differences between groups deserve investigation; they do not,
      on their own, explain why those differences exist.
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.subheader("A review in five steps")
steps = [
    ("01", "Understand the data", "See where the information comes from, what each field means, and who is represented."),
    ("02", "Evaluate the model", "Compare a simple baseline with candidate models and inspect the kinds of errors they make."),
    ("03", "Investigate group outcomes", "Look at rates and errors across groups, always alongside the number of examples."),
    ("04", "Experiment carefully", "Explore how changing a threshold affects different outcomes and their trade-offs."),
    ("05", "Review the findings", "Bring the evidence, methodology, and limitations together in one place."),
]
for start in range(0, len(steps), 2):
    columns = st.columns(2)
    for column, (number, title, description) in zip(columns, steps[start : start + 2]):
        with column:
            with st.container(border=True):
                st.caption(number)
                st.markdown(f"#### {title}")
                st.write(description)

st.caption(
    "Start with the pages in the sidebar. The application deliberately shows no model "
    "scores until the data and evaluation pipeline have been implemented and run."
)
