"""Shared fixtures. The data here are SYNTHETIC test fixtures, never shown as real results."""

import numpy as np
import pandas as pd
import pytest

CATEGORICAL = {
    "Attribute1": ["A11", "A12", "A13", "A14"],
    "Attribute3": ["A30", "A31", "A32", "A33", "A34"],
    "Attribute4": ["A40", "A41", "A42", "A43", "A49"],
    "Attribute6": ["A61", "A62", "A63", "A65"],
    "Attribute7": ["A71", "A72", "A73", "A74", "A75"],
    "Attribute9": ["A91", "A92", "A93", "A94"],
    "Attribute10": ["A101", "A102", "A103"],
    "Attribute12": ["A121", "A122", "A123", "A124"],
    "Attribute14": ["A141", "A142", "A143"],
    "Attribute15": ["A151", "A152", "A153"],
    "Attribute17": ["A171", "A172", "A173", "A174"],
    "Attribute19": ["A191", "A192"],
    "Attribute20": ["A201", "A202"],
}


def make_synthetic(n: int = 1000, seed: int = 0) -> pd.DataFrame:
    """Same schema as the UCI file (Attribute1..20 + class) with a learnable signal."""
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame(
        {
            "Attribute2": rng.integers(4, 73, n),
            "Attribute5": rng.integers(250, 18000, n),
            "Attribute8": rng.integers(1, 5, n),
            "Attribute11": rng.integers(1, 5, n),
            "Attribute13": np.clip(rng.gamma(6, 5.5, n), 19, 75).astype(int),
            "Attribute16": rng.integers(1, 5, n),
            "Attribute18": rng.integers(1, 3, n),
        }
    )
    for col, levels in CATEGORICAL.items():
        frame[col] = rng.choice(levels, n)
    logit = (
        -1.5 + 0.03 * (frame["Attribute2"] - 20) + 0.00006 * (frame["Attribute5"] - 3000)
        - 0.9 * (frame["Attribute1"] == "A14") + 0.5 * (frame["Attribute1"] == "A11")
        + 0.4 * (frame["Attribute13"] < 25) + rng.normal(0, 0.8, n)
    )
    frame["class"] = np.where(rng.random(n) < 1 / (1 + np.exp(-logit)), 2, 1)
    cols = [f"Attribute{i}" for i in range(1, 21)] + ["class"]
    return frame[cols]


@pytest.fixture(scope="session")
def synthetic_frame() -> pd.DataFrame:
    return make_synthetic()


@pytest.fixture()
def synthetic_csv(tmp_path, synthetic_frame):
    path = tmp_path / "german_credit.csv"
    synthetic_frame.to_csv(path, index=False)
    return path

