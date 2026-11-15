from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fairlens.applicant import age_flip_rate
from fairlens.config import AGE_COLUMN, PERSONAL_STATUS_COLUMN
from fairlens.data import group_labels
from fairlens.metrics import group_outcome_metrics
from fairlens.proxies import proxy_report
from fairlens.ui import (
    AMBER, GREEN, SAGE, Settings, callout, get_audit, get_op, header, require_data, setup_page, show_chart, show_table,
    sidebar, style,
)

setup_page("Proxy detector")
settings = sidebar()
header(
    "Proxy detector",
    "Removing a sensitive input does not remove what it tells the model. Here we test whether age can still be "
    "recovered from the other inputs, and whether deleting age actually changes outcomes.",
)
data = require_data()
YOUNG, OLD = group_labels()


@st.cache_data(show_spinner="Testing how well other inputs recover age group...")
def _proxy(_data, drop_status: bool, key: str):
    return proxy_report(_data, drop_status)


drop_status = st.toggle("Also hide personal status and sex from the detector", value=False, key="proxy_drop_status")
rep = _proxy(data, drop_status, f"{len(data)}-{st.session_state.get('use_demo_data', False)}")
auc = rep["overall_auc"]
level = "strong" if auc >= 0.8 else "moderate" if auc >= 0.65 else "weak"
c1, c2, c3 = st.columns(3)
c1.metric("Age group recoverable from other inputs", f"AUC {auc:.2f}", help="0.50 = no signal, 1.00 = perfectly recoverable. Cross-validated.")
c2.metric("Signal strength", level.title())
c3.metric(f"{YOUNG} in the data", f"{rep['n_young']} of {rep['n']}")
callout(
    "What this means",
    f"A simple model that never sees age can still tell the {YOUNG} group from the {OLD} group with AUC <b>{auc:.2f}</b> "
    f"({level} signal). So deleting age as an input is unlikely to stop a model using age-related information. "
    "<b>Interpretation:</b> this is a risk indicator, not proof that the real model discriminates.",
    "caution" if auc >= 0.65 else "note",
)

t = rep["per_feature"].head(8).iloc[::-1]
fig = go.Figure(go.Bar(x=t["auc"] - 0.5, y=t["feature"], orientation="h", marker_color=[AMBER if a >= 0.65 else SAGE for a in t["auc"]],
                       text=[f"AUC {a:.2f}" for a in t["auc"]], textposition="outside", base=0.5))
fig.update_xaxes(range=[0.45, 1.12], title="How well this ONE input alone recovers age group (AUC)")
st.subheader("Which inputs act as proxies?")
show_chart(style(fig, 360))
st.caption("Each bar is a model using a single input, scored by 5-fold cross-validation. Amber means 0.65 or higher.")

# ---- does removing age change outcomes? --------------------------------------------------------------------------
st.subheader("Does deleting the sensitive inputs change outcomes?")
op = get_op()
rows = []
for label, excl in (("Model sees age and status", ()), ("Age removed", (AGE_COLUMN,)), ("Age and status removed", (AGE_COLUMN, PERSONAL_STATUS_COLUMN))):
    a = get_audit(data, Settings(settings.model, excl))
    y, g, p = a.y("validation"), a.groups("validation"), a.proba(settings.model, "validation")
    m = group_outcome_metrics(y, op.apply(p, g), g).set_index("group")
    flip = age_flip_rate(a.pipelines[settings.model], a.splits.X_validation, op.threshold) if AGE_COLUMN not in excl else {"flip_rate": 0.0}
    rows.append({
        "Setup": label,
        f"Classified Good: {YOUNG}": m.loc[YOUNG, "predicted_good_rate"], f"Classified Good: {OLD}": m.loc[OLD, "predicted_good_rate"],
        "Gap (younger minus older)": m.loc[YOUNG, "predicted_good_rate"] - m.loc[OLD, "predicted_good_rate"],
        "Decisions flipped by changing only age": flip["flip_rate"],
    })
tbl = pd.DataFrame(rows)
for c in tbl.columns[1:]:
    tbl[c] = tbl[c].map(lambda v: f"{v:+.1%}" if "Gap" in c else f"{v:.1%}")
show_table(tbl)
st.markdown(
    f"- **Measured:** with age removed, the gap moves from **{rows[0]['Gap (younger minus older)']:+.1%}** to **{rows[1]['Gap (younger minus older)']:+.1%}** "
    f"(validation set, {op.describe()}).\n"
    f"- **Limitation:** the {YOUNG} group is small in the validation split, so gaps move a lot by chance. Check stability on the Group outcomes page.\n"
    "- **Takeaway:** if the gap barely moves when age is removed, the model is getting the information from somewhere else."
)
