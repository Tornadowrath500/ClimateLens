"""Built-in SYNTHETIC demo data with the UCI German Credit schema.

Used only so the app can be explored offline. It is invented, never real evidence, and the app
labels it as synthetic wherever it is used. Age is deliberately correlated with savings, employment
and property so the proxy tools have something to show.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_demo_dataset(n: int = 1000, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    age = np.clip(rng.gamma(7.5, 4.7, n), 19, 75).astype(int)
    young = age < 25
    pick = lambda levels, p: rng.choice(levels, n, p=np.asarray(p) / np.sum(p))
    pick_by_age = lambda levels, p_young, p_old: np.where(
        young, pick(levels, p_young), pick(levels, p_old)
    )
    f = pd.DataFrame({"Attribute13": age})
    f["Attribute1"] = pick(["A11", "A12", "A13", "A14"], [27, 27, 6, 40])
    f["Attribute2"] = np.clip(rng.lognormal(2.95, 0.55, n), 4, 72).astype(int)
    f["Attribute3"] = pick(["A30", "A31", "A32", "A33", "A34"], [4, 5, 53, 9, 29])
    f["Attribute4"] = pick(["A40", "A41", "A42", "A43", "A44", "A45", "A46", "A48", "A49", "A410"],
                           [23, 10, 18, 28, 1, 2, 5, 1, 10, 2])
    f["Attribute5"] = np.clip(rng.lognormal(7.9, 0.75, n) * (0.6 + f["Attribute2"] / 40), 250, 18500).astype(int)
    f["Attribute6"] = pick_by_age(["A61", "A62", "A63", "A64", "A65"], [75, 8, 3, 2, 12], [58, 11, 7, 6, 18])
    f["Attribute7"] = pick_by_age(["A71", "A72", "A73", "A74", "A75"], [10, 40, 38, 9, 3], [5, 15, 34, 18, 28])
    f["Attribute8"] = rng.choice([1, 2, 3, 4], n, p=[0.14, 0.23, 0.16, 0.47])
    f["Attribute9"] = np.where(young, pick(["A92", "A93", "A91", "A94"], [48, 40, 6, 6]),
                               pick(["A92", "A93", "A91", "A94"], [28, 55, 5, 12]))
    f["Attribute10"] = pick(["A101", "A102", "A103"], [91, 4, 5])
    f["Attribute11"] = np.where(young, rng.integers(1, 4, n), rng.integers(1, 5, n))
    f["Attribute12"] = pick_by_age(["A121", "A122", "A123", "A124"], [14, 22, 40, 24], [30, 23, 31, 16])
    f["Attribute14"] = pick(["A141", "A142", "A143"], [14, 5, 81])
    f["Attribute15"] = pick_by_age(["A151", "A152", "A153"], [45, 35, 20], [14, 77, 9])
    f["Attribute16"] = rng.choice([1, 2, 3, 4], n, p=[0.63, 0.33, 0.03, 0.01])
    f["Attribute17"] = pick(["A171", "A172", "A173", "A174"], [2, 20, 63, 15])
    f["Attribute18"] = rng.choice([1, 2], n, p=[0.85, 0.15])
    f["Attribute19"] = pick(["A191", "A192"], [60, 40])
    f["Attribute20"] = pick(["A201", "A202"], [96, 4])

    risk = (
        -1.55 + 0.028 * (f["Attribute2"] - 21) + 0.00007 * (f["Attribute5"] - 3200)
        + 0.95 * (f["Attribute1"] == "A11") + 0.45 * (f["Attribute1"] == "A12") - 0.95 * (f["Attribute1"] == "A14")
        + 0.55 * f["Attribute6"].isin(["A61"]) - 0.45 * f["Attribute6"].isin(["A64", "A65"])
        + 0.5 * f["Attribute3"].isin(["A33"]) - 0.55 * (f["Attribute3"] == "A34")
        + 0.35 * f["Attribute7"].isin(["A71", "A72"]) - 0.25 * (f["Attribute7"] == "A75")
        + 0.3 * (f["Attribute15"] == "A151") + 0.25 * (f["Attribute12"] == "A124")
        - 0.4 * (f["Attribute10"] == "A103") + 0.25 * (f["Attribute14"] == "A141")
        + 0.25 * young + rng.normal(0, 0.7, n)
    )
    f["class"] = np.where(rng.random(n) < 1 / (1 + np.exp(-risk)), 2, 1)
    cols = [f"Attribute{i}" for i in range(1, 21)] + ["class"]
    return f[cols]
