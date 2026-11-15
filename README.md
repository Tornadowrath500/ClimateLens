# FairLens

**Understand the decisions behind the model.**

FairLens is an educational, human-centered model-auditing prototype. It helps a reviewer inspect a historical credit-risk classifier, compare predictive performance, examine differences in model outcomes between groups, and test the trade-offs created by changes to a decision threshold.

> **Important:** This is an educational benchmark, not a lending system, credit recommendation, or financial advice. It must never be used to make decisions about real applicants.

## Product principles

- **Transparent:** Each result should identify its data source, model, evaluation split, metric definition, and relevant sample count.
- **Human-centered:** Explain findings in plain language before exposing technical detail.
- **Careful with fairness claims:** A measured difference is a signal to investigate, not proof of discrimination or its cause.
- **Honest about uncertainty:** Show denominators and uncertainty where appropriate. Do not collapse multiple dimensions into one unexplained fairness score.
- **Reproducible:** Keep preprocessing, model selection, and evaluation in explicit, testable Python modules.
- **No invented evidence:** Never display placeholder metrics as actual findings.

## Initial benchmark

The planned benchmark is the [UCI Statlog (German Credit Data)](https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data), donated in 1994. It contains 1,000 historical examples, 20 input features, and a binary target: 1 = Good, 2 = Bad. The source also provides a cost matrix in which classifying an actually Bad-risk applicant as Good has five times the cost of the reverse error.

The dataset's historical German context is a major limitation. It does not represent current lending practices or today's applicant population. See docs/DATA_AND_ETHICS.md.

## Intended user journey

1. **Understand the data** — inspect its source, target definition, feature types, missingness, and limitations.
2. **Evaluate the model** — compare a simple baseline with candidate classifiers on validation data; inspect the final test set only after pinning a configuration.
3. **Investigate group outcomes** — compare carefully defined group metrics, denominators, and uncertainty.
4. **Experiment** — explore threshold and mitigation trade-offs without presenting an experiment as a guaranteed fairness fix.
5. **Review findings** — summarize methods, results, and limitations in a reproducible report.

## Hands-on tools (pages 7 to 11)

| Page | What you can do |
| --- | --- |
| **Applicant map** | Every applicant is a dot placed by similarity (PCA of non-sensitive inputs). Colour by score, group, mistakes or label; overlay a *fairness terrain* of look-alike regions where the two age groups are classified differently (blank where counts are too small); click a dot for a "why this score" chart, a look-alike check and a what-if path. |
| **Applicant simulator** | Build a fictional applicant with sliders. Live score, per-input contributions, shortest what-if chain, and a twin test that changes only a sensitive input. |
| **Proxy detector** | Cross-validated test of whether age can be recovered from the other inputs, per-input proxy strength, and a with/without-age outcome comparison. |
| **Mitigation lab** | Baseline, cost-tuned threshold, input removal, reweighing and a group-threshold what-if on one cost-versus-gap map, with bootstrap intervals. |
| **Audit your own model** | Upload any CSV of decisions or scores plus a group column; get rates with intervals, error rates if truth is supplied, and plain-language findings. |

No internet? Use **Explore with synthetic demo data** (home or data page). It is invented data with the German Credit layout, labelled
`SYNTHETIC DEMO DATA` on every page and in downloaded reports. It is never real evidence.

New core modules (all unit-tested, no Streamlit imports): `applicant.py`, `mapview.py`, `proxies.py`, `mitigation.py`, `byom.py`, `demo.py`.

## Repository structure

```
.
├── app.py                  # Grouped Streamlit navigation and entry point
├── pages/                  # Overview, guided review, applicant exploration, and audit tools
├── src/fairlens/           # config, data, splitting, models, metrics, evaluation, report, ui
├── scripts/                # Explicit data acquisition
├── tests/                  # Unit tests + Streamlit smoke tests
├── docs/                   # Methodology, roadmap, handoff, submission guide
└── data/                   # Local data only; not committed
```

## Quick start

Python 3.11 or newer is recommended.

    python -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    pip install -e .
    python -m pytest
    streamlit run app.py

On Windows PowerShell, activate the environment with:

    .venv\Scripts\Activate.ps1

The application never downloads data silently or shows placeholder numbers. Fetch the benchmark with the button on the first page, or run:

    python scripts/download_dataset.py

The downloaded file and manifest remain local and are excluded from Git. See data/README.md.

## Evaluation commitments

- Use stratified training, validation, and final test sets; this is a static classification dataset, not a time-series forecasting task.
- Select models and thresholds using validation data. The final test set stays hidden until one deliberate review is pinned per app session; the Findings page uses that frozen snapshot.
- Compare against the competition's simple baseline: predict every applicant as Good credit risk. Confirm target encoding from the original UCI source.
- Report class-specific errors, especially the costlier error of predicting Good for an actually Bad case.
- Report group denominators. Avoid conclusions from tiny groups.
- Explain that group differences do not establish causation or legal discrimination.

## Current status

The application code includes baselines, Logistic Regression and Random Forest, the UCI cost matrix, an age-group audit with intervals and repeated-split sensitivity checks, a validation-only threshold lab, and a downloadable report. The core suite currently passes 33 tests; the Streamlit page smoke tests and real-data download still need verification in an environment with Streamlit and network access. See docs/HANDOFF.md for the verification record, and docs/SUBMISSION.md for the write-up and demo plan.

## Project licensing

The repository's own software license has **not** been selected yet. The dataset's CC BY 4.0 license is separate from the license for this project's code. The team should agree on a project license before adding one.
