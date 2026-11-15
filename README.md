# FairLens

**Understand the decisions behind a model.**

FairLens is an educational, interactive model-auditing app. Its main case study is the UCI Statlog (German Credit) benchmark: 1,000 historical records collected in Germany and donated in 1994. The app lets visitors inspect the data, compare model performance, explore group-level outcomes, test threshold and mitigation choices, and prepare a cautious evidence-based report.

**Live app:** https://fairlensinsight.streamlit.app/

> FairLens is not a lending system, credit recommendation, clinical tool, or professional advice. Its historical benchmark does not represent current applicants. Group gaps are prompts for investigation, not proof of discrimination or causation.

## Start here

The Streamlit app opens on the Home dashboard. It shows the active data source and offers a guided route:

1. **Data & scope** — inspect the benchmark, labels, feature dictionary, and limitations.
2. **Model performance** — compare predictive performance, baselines, error types, and the UCI cost matrix.
3. **Group outcomes** — compare rates with denominators and uncertainty.
4. **Claim checker** — stress-test common conclusions against the evidence they require.
5. **Experiment and mitigation labs** — explore how thresholds and input choices change measured outcomes.
6. **Findings & report** — create a report from a deliberately pinned final test review.

Other areas support applicant-level what-if exploration, proxy checks, an applicant map, and auditing an uploaded model. **Health equity lab** is a separate deterministic simulation with invented records; it illustrates how assumptions can change metrics and is not health data or a real clinical-model audit.

## Data and interpretation

- The primary dataset is the public UCI Statlog (German Credit Data), UCI ID 144. It is historical, small, and has known documentation/coding concerns; consult the app's Data & scope page and [Data and ethics](docs/DATA_AND_ETHICS.md).
- Labels are encoded as Good (1) and Bad (2). They are historical labels, not observed lending approvals.
- The cost matrix assigns cost 5 to a Bad-labelled record predicted Good and cost 1 to a Good-labelled record predicted Bad.
- The age grouping is an exploratory analysis choice, not a legal category.
- Synthetic demo records are invented and must never be presented as observed evidence.
- The Health equity lab is reproducible synthetic data. It does not establish anything about real patients, tools, or health systems.
- The app does not sync current applicant, lending, or patient information. Re-downloading the UCI benchmark does not make it current.

For claims, use the **Claim checker**, cite the source and analysis configuration, include group sizes and uncertainty, and distinguish observed differences from causal or legal conclusions.

## Run locally

Requires Python 3.11+ (the deployed Streamlit environment may differ; see current dependency files).

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

The repository includes the benchmark under `data/raw/`. To retrieve it again from UCI, use the data page or:

```bash
python scripts/download_dataset.py
```

Run the existing checks with:

```bash
python -m pytest
```

## Project map

- `app.py`: Streamlit entry point and page navigation.
- `pages/`: Streamlit pages, including Claim checker and Health equity lab.
- `src/fairlens/`: shared UI, data loading, metrics, evaluation, reports, and model logic.
- `data/raw/`: bundled historical benchmark and provenance manifest.
- `docs/`: ethics, API, continuity, roadmap, and submission guidance.
- `frontend/` and `backend/`: separate prototype components; they are not the entry point used by the Streamlit deployment.

## Deployment

The Streamlit Community Cloud app should be configured to use this repository, branch `main`, and `app.py`. GitHub Actions currently runs tests; that workflow is not the Streamlit deployment. Confirm deployments in Streamlit's app settings and logs. After a merge, verify the deployed revision and open the app to check the visible result.
