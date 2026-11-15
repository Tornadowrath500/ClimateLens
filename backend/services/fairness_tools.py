"""Proxy detector and mitigation lab."""

from __future__ import annotations

from backend import state
from backend.services.common import check_model, context, respond, source_info
from fairlens.applicant import age_flip_rate
from fairlens.config import AGE_COLUMN, PERSONAL_STATUS_COLUMN
from fairlens.data import group_labels
from fairlens.metrics import group_outcome_metrics
from fairlens.mitigation import build_strategies, evaluate_strategies
from fairlens.proxies import proxy_report


# ---- proxy detector --------------------------------------------------------------------------------------
def proxies_report(source: str = "real", drop_status: bool = False) -> dict:
    data, dkey = state.get_dataset(source)
    drop_status = bool(drop_status)
    rep = state.derived(("proxy", dkey, drop_status), lambda: proxy_report(data, drop_status))
    auc = rep["overall_auc"]
    return respond(source_info(source), {
        "overall_auc": auc, "level": "strong" if auc >= 0.8 else "moderate" if auc >= 0.65 else "weak",
        "per_feature": rep["per_feature"], "n_young": rep["n_young"], "n": rep["n"], "drop_status": drop_status,
        "young_label": group_labels()[0], "old_label": group_labels()[1],
    })


def proxies_removal(source: str = "real", model: str = "Logistic regression", decision_rule=None) -> dict:
    """Does deleting the sensitive inputs change outcomes? Same three set-ups the Streamlit page compared."""
    base = context(source, model, (), decision_rule)
    young, old = group_labels()
    rows = []
    for label, excl in (("Model sees age and status", ()), ("Age removed", (AGE_COLUMN,)),
                        ("Age and status removed", (AGE_COLUMN, PERSONAL_STATUS_COLUMN))):
        audit, _ = state.get_audit(source, excl)
        y, g, p = audit.y("validation"), audit.groups("validation"), audit.proba(model, "validation")
        m = group_outcome_metrics(y, base.op.apply(p, g), g).set_index("group")
        flip = (age_flip_rate(audit.pipelines[model], audit.splits.X_validation, base.op.threshold)["flip_rate"]
                if AGE_COLUMN not in excl else 0.0)
        ry = m.loc[young, "predicted_good_rate"] if young in m.index else None
        ro = m.loc[old, "predicted_good_rate"] if old in m.index else None
        rows.append({"setup": label, "rate_young": ry, "rate_old": ro,
                     "gap": (ry - ro) if ry is not None and ro is not None else None, "flip_rate": flip})
    return respond(base, {"split": "validation", "rows": rows, "young_label": young, "old_label": old})


# ---- mitigation lab ----------------------------------------------------------------------------------------
def mitigation_run(source: str = "real", model: str = "Logistic regression") -> dict:
    check_model(model)
    data, dkey = state.get_dataset(source)

    def build():
        strategies, y, g = build_strategies(data, model)
        return strategies, evaluate_strategies(strategies, y, g), len(y)

    strategies, table, n_val = state.derived(("mitigation", dkey, model), build)
    return respond(source_info(source), {
        "split": "validation", "model": model, "n_validation": n_val, "table": table,
        "strategies": [{"name": s.name, "blurb": s.blurb, "caution": s.caution} for s in strategies.values()],
    })