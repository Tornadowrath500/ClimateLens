"""Core tests for the hands-on tools. Data are SYNTHETIC fixtures, never shown as real results."""

import numpy as np
import pandas as pd

from fairlens import applicant as A, byom as B, mapview as M, mitigation as G, proxies as P
from fairlens.config import AGE_COLUMN, value_label
from fairlens.demo import make_demo_dataset
from fairlens.evaluation import OperatingPoint, run_audit
from fairlens.models import LOGISTIC


def _audit(excluded=()):
    return run_audit(make_demo_dataset(), excluded, 42, (LOGISTIC,))


def test_demo_dataset_matches_schema():
    d = make_demo_dataset()
    assert d.shape == (1000, 21) and set(d["class"]) == {1, 2}
    assert (d[AGE_COLUMN] >= 19).all()


def test_value_labels_fall_back_to_code():
    assert value_label("Attribute1", "A14") == "No checking account"
    assert value_label("Attribute1", "ZZZ") == "ZZZ"


def test_explain_and_counterfactuals():
    au = _audit(); pipe = au.pipelines[LOGISTIC]; row = au.splits.X_validation.iloc[[0]]
    e = A.explain(pipe, row, au.splits.X_train)
    assert len(e) == 20 and np.isfinite(e["contribution"]).all()
    steps, p, flipped = A.greedy_path(pipe, row, au.splits.X_train, 0.5)
    assert 0 <= p <= 1 and isinstance(flipped, bool)
    ch = A.best_single_changes(pipe, row, au.splits.X_train, 0.5)
    assert set(ch["column"]) <= set(A.ACTIONABLE_COLUMNS)


def test_excluded_age_has_zero_direct_effect():
    au = _audit((AGE_COLUMN,)); pipe = au.pipelines[LOGISTIC]
    assert A.age_flip_rate(pipe, au.splits.X_validation, 0.5)["flip_rate"] == 0.0
    tw = A.sensitive_flip_test(pipe, au.splits.X_validation.iloc[[1]], au.splits.X_train, 0.5)
    assert (tw[tw["changed_input"] == "Age (years)"]["change_vs_original"].abs() < 1e-12).all()


def test_map_and_terrain_hide_unreliable_cells():
    au = _audit(); md = M.build_map(au, LOGISTIC, OperatingPoint(0.5), include_train=True)
    assert len(md.frame) == len(md.X) == len(md.Z)
    t = M.terrain(md.frame, 5, 5)
    assert t.loc[~t["reliable"], "gap"].isna().all()
    assert M.terrain(md.frame, 5, 10_000)["reliable"].sum() == 0
    la = M.look_alikes(md, 0, 10)
    assert la["same"]["n"] == 10 and la["other"]["n"] == 10


def test_proxy_report_detects_correlated_inputs():
    r = P.proxy_report(make_demo_dataset())
    assert r["overall_auc"] > 0.65 and r["per_feature"]["auc"].is_monotonic_decreasing


def test_reweighing_balances_groups():
    y = np.array([1, 1, 1, 2, 1, 2, 2, 2]); g = np.array(list("aaaabbbb"))
    w = G.reweighing_weights(y, g)
    for grp in "ab":
        for lab in (1, 2):
            m = (g == grp) & (y == lab)
            assert abs(w[m].sum() / w.sum() - (g == grp).mean() * (y == lab).mean()) < 1e-9


def test_strategies_run_and_report_uncertainty():
    S, y, g = G.build_strategies(make_demo_dataset(), LOGISTIC)
    t = G.evaluate_strategies(S, y, g)
    assert len(t) == 6 and (t["gap_classified_good_lo"] <= t["gap_classified_good_hi"]).all()


def test_byo_group_table():
    fav = np.array([1] * 8 + [0] * 2 + [1] * 3 + [0] * 5, dtype=bool)
    groups = ["a"] * 10 + ["b"] * 8
    t = B.group_table(fav, groups)
    assert t.set_index("group").loc["a", "selection_rate"] == 0.8 and t["small_group"].all()
    assert t.set_index("group").loc["b", "ratio_to_reference"] < 0.8
    assert any("below 0.80" in x or "very uncertain" in x for x in B.plain_summary(t))
