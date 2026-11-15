import math
import re

import numpy as np
import pandas as pd
import pytest

from fairlens.baselines import predict_all_bad, predict_all_good
from fairlens.data import group_labels, load_dataset, make_age_groups
from fairlens.evaluation import OperatingPoint, repeat_split_gaps, run_audit, validation_comparison
from fairlens.metrics import (
    age_gap,
    best_threshold_by_cost,
    classification_summary,
    cost_per_applicant,
    group_outcome_metrics,
    intervals_overlap,
    predict_from_proba,
    theoretical_cost_threshold,
    threshold_sweep,
    uci_cost,
    wilson_interval,
)
from fairlens.models import FOREST, LOGISTIC, build_preprocessor, prob_good
from fairlens.report import compute_findings, compute_group_review, render_markdown
from fairlens.splitting import stratified_split


# --- cost matrix -----------------------------------------------------------------
def test_cost_matrix_penalizes_bad_predicted_good_five_times():
    assert uci_cost([2], [1]) == 5  # actually Bad, predicted Good
    assert uci_cost([1], [2]) == 1  # actually Good, predicted Bad
    assert uci_cost([1, 2], [1, 2]) == 0
    assert cost_per_applicant([2, 1], [1, 2]) == pytest.approx(3.0)


def test_theoretical_threshold_is_five_sixths():
    assert theoretical_cost_threshold() == pytest.approx(5 / 6)


def test_baselines_cost_on_known_labels():
    y = np.array([1] * 7 + [2] * 3)
    assert cost_per_applicant(y, predict_all_good(10)) == pytest.approx(1.5)
    assert cost_per_applicant(y, predict_all_bad(10)) == pytest.approx(0.7)


# --- classification summary ------------------------------------------------------
def test_summary_confusion_is_always_2x2_even_for_constant_predictions():
    s = classification_summary([1, 1, 2, 2], predict_all_good(4))
    assert s["confusion_matrix"] == [[2, 0], [2, 0]]
    assert s["recall"] == 1.0 and s["recall_other"] == 0.0
    assert math.isnan(s["auc"])


def test_summary_named_positive_class_is_good():
    s = classification_summary([1, 1, 2, 2], [1, 2, 1, 2])
    assert s["precision"] == pytest.approx(0.5) and s["recall"] == pytest.approx(0.5)
    assert s["confusion"] == {"good_as_good": 1, "good_as_bad": 1, "bad_as_good": 1, "bad_as_bad": 1}


def test_predict_from_proba_threshold_is_inclusive():
    assert predict_from_proba([0.4, 0.5, 0.6], 0.5).tolist() == [2, 1, 1]


# --- intervals and group metrics -------------------------------------------------
def test_wilson_interval_basic_properties():
    low, high = wilson_interval(5, 10)
    assert 0 < low < 0.5 < high < 1
    assert all(math.isnan(x) for x in wilson_interval(0, 0))
    assert wilson_interval(0, 20)[0] == 0.0
    assert wilson_interval(20, 20)[1] == 1.0


def test_group_metrics_report_counts_and_intervals():
    r = group_outcome_metrics([1, 1, 2, 2, 2], [1, 2, 1, 1, 2], ["A", "A", "B", "B", "B"]).set_index("group")
    assert r.loc["B", "false_good_count"] == 2 and r.loc["B", "actual_bad_count"] == 3
    assert r.loc["B", "false_good_rate_among_bad"] == pytest.approx(2 / 3)
    assert r.loc["B", "false_good_ci_low"] < 2 / 3 < r.loc["B", "false_good_ci_high"]
    assert r.loc["A", "cost_per_applicant"] == pytest.approx(0.5)


def test_age_gap_is_younger_minus_older_and_overlap_helper():
    m = group_outcome_metrics([1, 1, 1, 1], [1, 2, 1, 1], ["Under 25", "Under 25", "25 or older", "25 or older"])
    assert age_gap(m, "Under 25", "25 or older")["predicted_good_rate"] == pytest.approx(-0.5)
    assert age_gap(m, "Under 25", "missing")["predicted_good_rate"] != age_gap(m, "Under 25", "missing")["predicted_good_rate"]
    assert intervals_overlap((0.1, 0.4), (0.3, 0.6)) and not intervals_overlap((0.1, 0.2), (0.3, 0.6))


def test_threshold_sweep_is_monotone_and_has_group_rows():
    rng = np.random.default_rng(1)
    p = rng.random(200)
    y = np.where(rng.random(200) < p, 1, 2)
    g = np.where(rng.random(200) < 0.2, "Under 25", "25 or older")
    sweep = threshold_sweep(y, p, g)
    assert set(sweep["group"]) == {"All", "Under 25", "25 or older"}
    rates = sweep[sweep["group"] == "All"].sort_values("threshold")["predicted_good_rate"].to_numpy()
    assert (np.diff(rates) <= 1e-12).all()  # raising the threshold never adds Good predictions


def test_best_threshold_by_cost_prefers_high_threshold_for_5_to_1_costs():
    rng = np.random.default_rng(2)
    p = rng.random(2000)
    y = np.where(rng.random(2000) < p, 1, 2)  # perfectly calibrated
    t, _ = best_threshold_by_cost(y, p)
    assert 0.7 < t < 0.95


# --- data, splits, leakage -------------------------------------------------------
def test_load_dataset_and_age_groups(synthetic_csv):
    data = load_dataset(synthetic_csv)
    young, old = group_labels()
    assert set(make_age_groups(data["Attribute13"])) <= {young, old}
    assert data["class"].dtype.kind == "i"


def test_load_dataset_missing_file_gives_actionable_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="download_dataset"):
        load_dataset(tmp_path / "nope.csv")


def test_split_is_reproducible_disjoint_and_stratified_by_group(synthetic_frame):
    X, y = synthetic_frame.drop(columns="class"), synthetic_frame["class"]
    strata = y.astype(str) + "|" + make_age_groups(X["Attribute13"])
    a = stratified_split(X, y, strata=strata)
    b = stratified_split(X, y, strata=strata)
    assert a.X_test.index.equals(b.X_test.index)
    parts = [set(a.X_train.index), set(a.X_validation.index), set(a.X_test.index)]
    assert not (parts[0] & parts[1] or parts[0] & parts[2] or parts[1] & parts[2])
    assert sum(map(len, parts)) == len(X)
    share = lambda s: (make_age_groups(s["Attribute13"]) == "Under 25").mean()
    assert abs(share(a.X_test) - share(X)) < 0.03


def test_preprocessing_is_fitted_on_training_data_only(synthetic_frame):
    audit = run_audit(synthetic_frame, models=(LOGISTIC,))
    scaler = audit.pipelines[LOGISTIC].named_steps["preprocess"].named_transformers_["numeric"]
    cols = list(scaler.feature_names_in_)
    assert np.allclose(scaler.mean_, audit.splits.X_train[cols].mean().to_numpy())
    assert not np.allclose(scaler.mean_, audit.splits.X_test[cols].mean().to_numpy())


def test_excluded_columns_never_reach_the_model(synthetic_frame):
    X = synthetic_frame.drop(columns="class")
    pre = build_preprocessor(X, exclude=("Attribute13", "Attribute9")).fit(X)
    names = " ".join(pre.get_feature_names_out())
    assert "Attribute13" not in names and "Attribute9" not in names and "Attribute2" in names


# --- audit end to end ------------------------------------------------------------
@pytest.fixture(scope="module")
def audit(synthetic_frame):
    return run_audit(synthetic_frame)


def test_audit_probabilities_are_valid_and_model_beats_chance(audit):
    p = audit.proba(LOGISTIC, "validation")
    assert p.min() >= 0 and p.max() <= 1 and len(p) == len(audit.y("validation"))
    table = validation_comparison(audit).set_index("model")
    assert table.loc[LOGISTIC, "auc"] > 0.6
    assert table.loc["All-Good baseline", "recall"] == 1.0


def test_logistic_and_forest_are_reproducible(synthetic_frame, audit):
    again = run_audit(synthetic_frame)
    for name in (LOGISTIC, FOREST):
        assert np.allclose(audit.proba(name, "validation"), again.proba(name, "validation"))


def test_per_group_thresholds_change_only_the_targeted_group():
    p = np.array([0.6, 0.6, 0.6, 0.6])
    groups = ["Under 25", "Under 25", "25 or older", "25 or older"]
    out = OperatingPoint(0.5, {"Under 25": 0.7}).apply(p, groups)
    assert out.tolist() == [2, 2, 1, 1]


def test_exploratory_group_review_reads_validation_only(audit, monkeypatch):
    original_y = audit.y
    original_groups = audit.groups
    original_proba = audit.proba

    def guarded_y(part):
        assert part == "validation", "exploratory group review must not inspect the final test labels"
        return original_y(part)

    def guarded_groups(part):
        assert part == "validation", "exploratory group review must not inspect the final test groups"
        return original_groups(part)

    def guarded_proba(model_name, part):
        assert part == "validation", "exploratory group review must not inspect final test probabilities"
        return original_proba(model_name, part)

    monkeypatch.setattr(audit, "y", guarded_y)
    monkeypatch.setattr(audit, "groups", guarded_groups)
    monkeypatch.setattr(audit, "proba", guarded_proba)

    review = compute_group_review(audit, LOGISTIC, OperatingPoint(0.5))
    assert review["part"] == "validation"
    assert set(review["groups"]["group"]) == {"Under 25", "25 or older"}
    assert review["n_young"] + review["n_old"] == len(audit.y("validation"))


def test_findings_and_report_contain_only_real_numbers(audit):
    f = compute_findings(audit, LOGISTIC, OperatingPoint(0.5))
    md = render_markdown(f)
    assert not re.search(r"\bnan\b", md.lower())  # no NaN leaked into prose
    for heading in ("## Setup", "## Group outcomes by age", "## Limitations", "## Citation"):
        assert heading in md
    assert f["n_train"] + f["n_validation"] + f["n_test"] == 1000


def test_repeat_split_gaps_returns_one_row_per_seed(synthetic_frame):
    out = repeat_split_gaps(synthetic_frame, LOGISTIC, seeds=range(3))
    assert len(out) == 3 and out["young_test_count"].min() > 10
    assert out["predicted_good_gap"].notna().all()

