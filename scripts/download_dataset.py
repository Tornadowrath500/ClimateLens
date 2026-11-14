"""Explicitly download the UCI German Credit benchmark to data/raw/."""

from __future__ import annotations

from fairlens.data import download_dataset


def main() -> None:
    frame = download_dataset()
    print(f"Saved {len(frame):,} rows and {frame.shape[1] - 1} features to data/raw/german_credit.csv")
    print(frame["class"].value_counts().sort_index().rename(index={1: "Good (1)", 2: "Bad (2)"}))


if __name__ == "__main__":
    main()
