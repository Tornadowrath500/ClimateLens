"""Turn pandas/numpy results into strict JSON-safe Python values (NaN and inf become null)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def jsonable(obj):
    if obj is None or isinstance(obj, (str, bool)):
        return obj
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, (int, np.integer)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        value = float(obj)
        return value if math.isfinite(value) else None
    if isinstance(obj, pd.DataFrame):
        return [jsonable(row) for row in obj.to_dict(orient="records")]
    if isinstance(obj, pd.Series):
        return jsonable(obj.to_dict())
    if isinstance(obj, dict):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return jsonable(obj.tolist())
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    try:
        if pd.isna(obj):
            return None
    except (TypeError, ValueError):
        pass
    return str(obj)