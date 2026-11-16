import pytest

from fairlens.baselines import predict_all_good


def test_all_good_baseline_returns_label_one() -> None:
    assert predict_all_good(4).tolist() == [1, 1, 1, 1]


def test_all_good_baseline_accepts_zero_rows() -> None:
    assert predict_all_good(0).size == 0


def test_all_good_baseline_rejects_negative_size() -> None:
    with pytest.raises(ValueError):
        predict_all_good(-1)

