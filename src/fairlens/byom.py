"""Audit ANY model's decisions: upload predictions + a group column, get a transparent group comparison."""

from __future__ import annotations

import numpy as np
import pandas as pd

from fairlens.metrics import wilson_interval

SMALL_GROUP = 30
FOUR_FIFTHS = 0.8  # a common screening heuristic from US employment guidance; NOT a legal test of discrimination here


def to_favorable(series: pd.Series, favorable_value=None, threshold: float = 0.5) -> np.ndarray:
    """Boolean 'favorable outcome' from a binary label column (given its favorable value) or a score column."""
    s = series.reset_index(drop=True)
    if favorable_value is None:
        return pd.to_numeric(s, errors="raise").to_numpy() >= threshold
    return (s.astype(str) == str(favorable_value)).to_numpy()


def group_table(favorable: np.ndarray, groups, actual_positive: np.ndarray | None = None, reference: str | None = None) -> pd.DataFrame:
    """Per-group selection rate (+95% interval), error rates when truth is supplied, and ratio to a reference group."""
    g = pd.Series(groups, dtype="object").fillna("Missing").astype(str).reset_index(drop=True)
    rows = []
    for name in sorted(g.unique()):
        m = (g == name).to_numpy()
        n, k = int(m.sum()), int(favorable[m].sum())
        lo, hi = wilson_interval(k, n)
        row = {"group": name, "n": n, "favorable": k, "selection_rate": k / n if n else np.nan, "ci_low": lo, "ci_high": hi}
        if actual_positive is not None:
            pos, neg = m & actual_positive, m & ~actual_positive
            row["true_positive_rate"] = float(favorable[pos].mean()) if pos.any() else np.nan
            row["false_positive_rate"] = float(favorable[neg].mean()) if neg.any() else np.nan
            row["precision"] = float(actual_positive[m & favorable].mean()) if (m & favorable).any() else np.nan
            row["n_actual_positive"], row["n_actual_negative"] = int(pos.sum()), int(neg.sum())
        rows.append(row)
    t = pd.DataFrame(rows)
    ref = reference if reference in set(t["group"]) else t.loc[t["n"].idxmax(), "group"]
    ref_rate = float(t.loc[t["group"] == ref, "selection_rate"].iloc[0])
    t["reference"] = ref
    t["ratio_to_reference"] = t["selection_rate"] / ref_rate if ref_rate > 0 else np.nan
    t["rate_difference"] = t["selection_rate"] - ref_rate
    t["small_group"] = t["n"] < SMALL_GROUP
    t["below_four_fifths"] = (t["ratio_to_reference"] < FOUR_FIFTHS) & (t["group"] != ref)
    return t


def plain_summary(t: pd.DataFrame) -> list[str]:
    """Plain-language observations. Descriptive only."""
    ref = t["reference"].iloc[0]
    lines = []
    for _, r in t[t["group"] != ref].iterrows():
        lines.append(
            f"**Measured:** {r['group']} received the favorable outcome {r['selection_rate']:.1%} of the time "
            f"({int(r['favorable'])} of {int(r['n'])}) versus {t.loc[t['group'] == ref, 'selection_rate'].iloc[0]:.1%} for {ref}: "
            f"a ratio of {r['ratio_to_reference']:.2f}."
        )
        if r["small_group"]:
            lines.append(f"**Limitation:** {r['group']} has only {int(r['n'])} rows, so this rate is very uncertain.")
        elif r["below_four_fifths"]:
            lines.append(f"**Signal:** the ratio for {r['group']} is below 0.80, a common screening heuristic. It flags a gap to investigate, not proof of discrimination.")
    return lines
