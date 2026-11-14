"""Simple benchmark baselines."""

from __future__ import annotations

import numpy as np

from fairlens.config import GOOD_RISK_LABEL


def predict_all_good(sample_count: int) -> np.ndarray:
    """Competition baseline: predict every case as Good (UCI label 1)."""
    if sample_count < 0:
        raise ValueError("sample_count cannot be negative.")
    return np.full(sample_count, GOOD_RISK_LABEL, dtype=int)
