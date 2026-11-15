# Bundled benchmark data

The app includes raw/german_credit.csv, a copy of the UCI Statlog (German Credit Data) benchmark, and raw/dataset_manifest.json with its source, attribution, license, retrieval time, target encoding, and row/feature counts. New users can open the app without downloading data or needing network access.

The benchmark is shared under the UCI dataset's CC BY 4.0 license. See [the dataset page](https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data) and [project data and ethics notes](../docs/DATA_AND_ETHICS.md).

The acquisition script remains available to refresh a local copy:

    python scripts/download_dataset.py

Do not add private, applicant-supplied, or otherwise restricted records to this directory or Git.

