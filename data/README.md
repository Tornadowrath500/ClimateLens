# Local data directory

The raw benchmark is deliberately not committed to Git.

Run from the repository root:

    python scripts/download_dataset.py

This writes:
- raw/german_credit.csv
- raw/dataset_manifest.json

Both are ignored by Git. The manifest records the dataset source, attribution, retrieval time, target encoding, and row/feature counts.

Do not place real applicant records, private information, credentials, or unrelated datasets here. Review the UCI CC BY 4.0 terms before redistributing derived material.
