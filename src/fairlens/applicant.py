"""Single-applicant tools: why a score, illustrative what-ifs, and sensitive-input probes.

Everything here is model-agnostic (it only calls predict_proba), so it works for any fitted pipeline.
These are *illustrations of model behaviour*, not advice to applicants or lending recommendations.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype

from fairlens.config import (
    ACTIONABLE_COLUMNS, AGE_COLUMN, PERSONAL_STATUS_COLUMN, feature_label, value_label,
)
from fairlens.models import prob_good

FOREIGN_COLUMN = "Attribute20"


def _repeat(row: pd.DataFrame, n: int) -> pd.DataFrame:
    return pd.concat([row] * n, ignore_index=True)


def score(pipeline, row: pd.DataFrame) -> float:
    return float(prob_good(pipeline, row.reset_index(drop=True))[0])


def explain(pipeline, row: pd.DataFrame, background: pd.DataFrame, k: int = 40, seed: int = 0) -> pd.DataFrame:
    """Contribution of each input = score minus the average score when that one input is swapped
    for values from other applicants (marginal occlusion). Positive pushes toward Good."""
    row = row.reset_index(drop=True)
    bg = background.sample(min(k, len(background)), random_state=seed).reset_index(drop=True)
    cols = list(row.columns)
    base = score(pipeline, row)
    blocks = []
    for c in cols:
        block = _repeat(row, len(bg))
        block[c] = bg[c].to_numpy()
        blocks.append(block)
    swapped = prob_good(pipeline, pd.concat(blocks, ignore_index=True)).reshape(len(cols), len(bg)).mean(axis=1)
    out = pd.DataFrame({"column": cols, "contribution": base - swapped})
    out["feature"] = out["column"].map(feature_label)
    out["value"] = [value_label(c, row.iloc[0][c]) for c in cols]
    out["abs"] = out["contribution"].abs()
    return out.sort_values("abs", ascending=False).drop(columns="abs").reset_index(drop=True)


def candidate_values(column: str, background: pd.DataFrame) -> list:
    s = background[column]
    if is_numeric_dtype(s):
        return sorted({int(round(v)) for v in np.quantile(s, np.linspace(0, 1, 21))})
    return sorted(s.unique())


def best_single_changes(pipeline, row, background, threshold: float, features=ACTIONABLE_COLUMNS) -> pd.DataFrame:
    """For each input, the single alternative value that moves the score furthest toward a flip."""
    row = row.reset_index(drop=True)
    p0 = score(pipeline, row)
    toward_good = p0 < threshold
    sign = 1 if toward_good else -1
    rows = []
    for c in features:
        if c not in row.columns:
            continue
        current = row.iloc[0][c]
        vals = [v for v in candidate_values(c, background) if v != current]
        if not vals:
            continue
        block = _repeat(row, len(vals))
        block[c] = vals
        p = prob_good(pipeline, block)
        j = int(np.argmax(sign * p))
        rows.append({
            "column": c, "feature": feature_label(c), "from": value_label(c, current), "to": value_label(c, vals[j]),
            "raw_to": vals[j], "p_before": p0, "p_after": float(p[j]), "flips": bool((p[j] >= threshold) != (p0 >= threshold)),
        })
    table = pd.DataFrame(rows, columns=["column", "feature", "from", "to", "raw_to", "p_before", "p_after", "flips"])
    return table.assign(gain=(sign * (table["p_after"] - table["p_before"]))).sort_values("gain", ascending=False).reset_index(drop=True)


def greedy_path(pipeline, row, background, threshold: float, features=ACTIONABLE_COLUMNS, max_steps: int = 3):
    """Smallest chain (up to max_steps single-input changes, chosen greedily) that flips the decision."""
    cur = row.reset_index(drop=True).copy()
    p0 = score(pipeline, cur)
    sign = 1 if p0 < threshold else -1
    used, steps, p = [], [], p0
    for _ in range(max_steps):
        table = best_single_changes(pipeline, cur, background, threshold, [f for f in features if f not in used])
        if table.empty or table.iloc[0]["gain"] <= 1e-9:
            break
        best = table.iloc[0]
        cur.loc[0, best["column"]] = best["raw_to"]
        used.append(best["column"])
        p = score(pipeline, cur)
        steps.append({"feature": best["feature"], "from": best["from"], "to": best["to"], "p_after": p})
        if (p >= threshold) != (p0 >= threshold):
            break
    flipped = (p >= threshold) != (p0 >= threshold)
    return pd.DataFrame(steps, columns=["feature", "from", "to", "p_after"]), p, bool(flipped)


def sensitive_flip_test(pipeline, row, background, threshold: float, young_age: int = 22, old_age: int = 40) -> pd.DataFrame:
    """Change ONE sensitive input, keep everything else fixed, and record the score.
    A zero change means the model does not use that input directly (it can still use proxies)."""
    row = row.reset_index(drop=True)
    p0 = score(pipeline, row)
    variants = [(AGE_COLUMN, f"Age {a}", a) for a in (young_age, old_age)]
    variants += [(PERSONAL_STATUS_COLUMN, value_label(PERSONAL_STATUS_COLUMN, v), v) for v in sorted(background[PERSONAL_STATUS_COLUMN].unique())]
    variants += [(FOREIGN_COLUMN, f"Foreign worker: {value_label(FOREIGN_COLUMN, v)}", v) for v in sorted(background[FOREIGN_COLUMN].unique())]
    out = []
    for col, label, v in variants:
        r = row.copy()
        r.loc[0, col] = v
        p = score(pipeline, r)
        out.append({"changed_input": feature_label(col), "variant": label, "p_good": p, "change_vs_original": p - p0,
                    "decision": "Good" if p >= threshold else "Bad", "decision_changes": bool((p >= threshold) != (p0 >= threshold))})
    return pd.DataFrame(out)


def age_flip_rate(pipeline, X: pd.DataFrame, threshold: float, young_age: int = 22, old_age: int = 40) -> dict:
    """Share of applicants whose classification flips when ONLY the age input is changed."""
    Xy, Xo = X.copy(), X.copy()
    Xy[AGE_COLUMN], Xo[AGE_COLUMN] = young_age, old_age
    py, po = prob_good(pipeline, Xy), prob_good(pipeline, Xo)
    return {
        "flip_rate": float(np.mean((py >= threshold) != (po >= threshold))),
        "mean_score_gain_if_older": float(np.mean(po - py)),
        "n": int(len(X)),
    }

