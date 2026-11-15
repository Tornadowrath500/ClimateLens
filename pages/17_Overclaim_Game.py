from __future__ import annotations

import streamlit as st

from fairlens.ui import callout, header, setup_page

setup_page("Over-claim game")
header(
    "The over-claim game",
    "Eight statements people make about audits. Decide: can an audit like this support it, or does it need more evidence?",
)

# (statement, supported?, explanation)
ROUNDS = [
    ("Group A is classified Good less often than Group B in this validation sample.", True,
     "A measured difference in a sample, reported with its group sizes, is exactly what an audit can show."),
    ("The model is biased against Group A.", False,
     "“Biased” is a causal and sometimes legal judgement. A rate gap is a signal to investigate, not proof of why."),
    ("Dropping the age column proves age no longer influences decisions.", False,
     "Other inputs can carry the same information, so a proxy test is needed before saying so."),
    ("A group with fewer records has a wider confidence interval for the same rate.", True,
     "That is a statistical property: less data means more uncertainty about the true rate."),
    ("These 1994 results show how lenders treat applicants today.", False,
     "The benchmark is historical and small. It cannot speak for current lenders, applicants, or other countries."),
    ("Moving a threshold to narrow a gap can also change the total cost of errors.", True,
     "Trade-offs between gaps, accuracy and cost are what the experiment and mitigation labs show."),
    ("The synthetic health lab proves screening tools miss more patients from one group.", False,
     "Every record in that lab is simulated. It illustrates a mechanism; it is not evidence about real patients or tools."),
    ("Sensitivity is the share of actual positive cases that a screen flags.", True,
     "That is the definition, which is why the lab reports it by group with its caveats."),
]
ss = st.session_state
ss.setdefault("og_i", 0)
ss.setdefault("og_score", 0)
ss.setdefault("og_pick", None)
ss.setdefault("og_streak", 0)


def answer(pick: bool) -> None:
    ss["og_pick"] = pick
    right = pick == ROUNDS[ss["og_i"]][1]
    ss["og_score"] += int(right)
    ss["og_streak"] = ss["og_streak"] + 1 if right else 0


def advance() -> None:
    ss["og_i"] += 1
    ss["og_pick"] = None


def restart() -> None:
    ss["og_i"], ss["og_score"], ss["og_pick"], ss["og_streak"] = 0, 0, None, 0


i, total = ss["og_i"], len(ROUNDS)
if i >= total:
    score = ss["og_score"]
    verdict = "You separate measured results from over-claims well." if score >= 6 else "Re-read the explanations above and try again."
    st.markdown(f'<div class="fl-verdict"><strong>Final score: {score} of {total}</strong><div class="fl-meter"><i style="width:{100 * score // total}%"></i></div>{verdict}</div>', unsafe_allow_html=True)
    st.button("Play again", on_click=restart, icon=":material/replay:")
else:
    st.progress(i / total, text=f"Round {i + 1} of {total} · score {ss['og_score']} · streak {ss['og_streak']}")
    statement, supported, why = ROUNDS[i]
    st.markdown(f'<div class="fl-statement">“{statement}”</div>', unsafe_allow_html=True)
    if ss["og_pick"] is None:
        a, b = st.columns(2)
        a.button("An audit can support this", on_click=answer, args=(True,), use_container_width=True, icon=":material/check_circle:")
        b.button("It needs more evidence", on_click=answer, args=(False,), use_container_width=True, icon=":material/help:")
    else:
        right = ss["og_pick"] == supported
        (st.success if right else st.error)(("Correct. " if right else "Not quite. ") + why)
        st.button("Next statement" if i + 1 < total else "See my score", on_click=advance, type="primary", icon=":material/arrow_forward:")

callout("About this game", "The statements are teaching examples about reading audits, not claims about any specific system.")

