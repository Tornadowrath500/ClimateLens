import math

import pandas as pd
import pytest

from fairlens.metrics import group_outcome_metrics


def test_group_metrics_include_denominators_and_clear_rates() -> None:
    result = group_outcome_metrics(
        y_true=[1, 1, 2, 2],
        y_pred=[1, 2, 1, 2],
        groups=["A", "A", "B", "B"],
    ).set_index("group")

    assert result.loc["A", "sample_count"] == 2
    assert result.loc["A", "predicted_good_rate"] == pytest.approx(0.5)
    assert result.loc["B", "false_good_rate_among_bad"] == pytest.approx(0.5)
    assert result.loc["A", "false_bad_rate_among_good"] == pytest.approx(0.5)


def test_group_metrics_reset_original_series_index() -> None:
    result = group_outcome_metrics(
        y_true=pd.Series([1, 1, 2, 2], index=[10, 11, 12, 13]),
        y_pred=[1, 2, 1, 2],
        groups=pd.Series(["A", "A", "B", "B"], index=[10, 11, 12, 13]),
    ).set_index("group")

    assert result.loc["A", "sample_count"] == 2
    assert result.loc["B", "sample_count"] == 2
    assert result.loc["B", "false_good_rate_among_bad"] == pytest.approx(0.5)


def test_group_metrics_show_nan_when_denominator_is_missing() -> None:
    result = group_outcome_metrics(
        y_true=[1, 1],
        y_pred=[1, 2],
        groups=["A", "A"],
    ).iloc[0]

    assert math.isnan(result["false_good_rate_among_bad"])


def test_group_metrics_reject_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same number"):
        group_outcome_metrics([1, 2], [1, 2], ["A"])

