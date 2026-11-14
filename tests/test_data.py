import pandas as pd
import pytest

from fairlens.data import make_age_groups, validate_dataset


def valid_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Attribute13": [19, 25, 42],
            "class": [1, 2, 1],
            "Attribute2": [12, 24, 36],
        }
    )


def test_validate_dataset_accepts_expected_schema() -> None:
    result = validate_dataset(valid_frame())
    assert len(result) == 3
    assert result["class"].tolist() == [1, 2, 1]


def test_validate_dataset_rejects_unexpected_target_labels() -> None:
    frame = valid_frame()
    frame.loc[0, "class"] = 0
    with pytest.raises(ValueError, match="target labels"):
        validate_dataset(frame)


def test_make_age_groups_uses_documented_boundary() -> None:
    groups = make_age_groups(pd.Series([24, 25, 30]))
    assert groups.tolist() == ["Under 25", "25 or older", "25 or older"]
