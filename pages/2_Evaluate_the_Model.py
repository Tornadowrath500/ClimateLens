from __future__ import annotations

import streamlit as st

from fairlens.config import DEFAULT_THRESHOLD
from fairlens.evaluation import validation_comparison
from fairlens.metrics import classification_summary, predict_from_proba
from fairlens.models import MODEL_NAMES
from fairlens.ui import (
    METRIC_HELP, callout, confusion_chart, cost_chart, get_audit, header, require_data, setup_page, show_chart,
    show_table, sidebar,
)

setup_page("Evaluate the model")
settings = sidebar()
header(
    "Evaluate the model",
    "Ask first how the model compares with doing almost nothing, and which of its mistakes are the expensive ones.",
)
data = require_data()
audit = get_audit(data, settings)
table = validation_comparison(audit, DEFAULT_THRESHOLD)
rows = table.set_index("model")

st.subheader("Start with simple baselines")
st.write(
    "The competition baseline predicts Good for everyone. We also show the opposite, rejecting everyone, as a reference "
    "only: it shows what the cost matrix rewards. These scores come from the **validation set**, which is where models "
    "are compared."
)
show_chart(cost_chart(table))
all_good, all_bad = rows.loc["All-Good baseline", "cost_per_applicant"], rows.loc["All-Bad (reference only)", "cost_per_applicant"]
best = max(MODEL_NAMES, key=lambda m: rows.loc[m, "auc"])
callout(
    "What this tells us",
    f"Predicting Good for everyone costs {all_good:.2f} per applicant; rejecting everyone costs {all_bad:.2f}. "
    f"Because a Bad case called Good costs five times more, a cautious rule can beat an accurate-looking one. "
    f"On validation data, {best.lower()} ranks applicants best (AUC {rows.loc[best, 'auc']:.2f}).",
)
with st.expander("Full comparison table (validation set, threshold 0.50)"):
    show_table(table.round(3))

st.subheader(f"{settings.model} on the validation set")
st.write(
    "Use this split to inspect the selected model and compare possible settings. The final test set stays hidden until "
    "you deliberately pin a decision rule in the Experiment lab."
)
y, p = audit.y("validation"), audit.proba(settings.model, "validation")
s = classification_summary(y, predict_from_proba(p, DEFAULT_THRESHOLD), p_good=p)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Accuracy", f"{s['accuracy']:.1%}", help=METRIC_HELP["accuracy"])
c2.metric("Good cases found", f"{s['recall']:.1%}", help=METRIC_HELP["recall_good"])
c3.metric("Bad cases caught", f"{s['recall_other']:.1%}", help=METRIC_HELP["recall_bad"])
c4.metric("Cost per applicant", f"{s['cost_per_applicant']:.2f}", help=METRIC_HELP["cost"])

left, right = st.columns([3, 2])
with left:
    show_chart(confusion_chart(s["confusion_matrix"]))
with right:
    missed = s["confusion"]["bad_as_good"]
    total_bad = missed + s["confusion"]["bad_as_bad"]
    callout(
        "Where it goes wrong",
        f"Of {total_bad} validation cases labelled Bad, the model called {missed} Good. Those are the expensive mistakes. "
        f"It also called {s['confusion']['good_as_bad']} Good cases Bad.",
        "caution",
    )
with st.expander("What do these terms mean?"):
    for key, label in (("accuracy", "Accuracy"), ("precision_good", f"Precision (Good): {s['precision']:.1%}"),
                       ("recall_good", "Recall (Good)"), ("recall_bad", "Recall (Bad)"),
                       ("f1", f"F1 (Good): {s['f1']:.2f}"), ("auc", f"AUC: {s['auc']:.2f}"), ("cost", "Cost per applicant")):
        st.markdown(f"**{label}.** {METRIC_HELP[key]}")

