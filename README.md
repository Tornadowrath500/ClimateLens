# FairLens

**Understand the decisions behind a model.**

FairLens is an educational, interactive model-auditing app. Its reproducible model-audit case study uses the UCI Statlog (German Credit) benchmark: 1,000 historical records collected in Germany and donated in 1994. Alongside that old benchmark, the app now explores current U.S. mortgage-application patterns from HMDA and recent consumer complaint aggregates from the CFPB. The live sources add contemporary financial context; they do not silently replace UCI or claim to measure the same thing.

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

Other areas support applicant-level what-if exploration, proxy checks, an applicant map, and auditing an uploaded model. **Mortgage application outcomes** compares recent HMDA mortgage action codes by reported race, ethnicity, or sex, with nationwide or state filters. **Live consumer signals** adds recent CFPB complaint aggregates. Both pages are separate from the UCI model metrics and state their source limits. **Health equity lab** is a separate deterministic simulation with invented records; it illustrates how assumptions can change metrics and is not health data or a real clinical-model audit.

## Data and interpretation

- The primary dataset is the public UCI Statlog (German Credit Data), UCI ID 144. It is historical, small, and has known documentation/coding concerns; consult the app's Data & scope page and [Data and ethics](docs/DATA_AND_ETHICS.md).
- Labels are encoded as Good (1) and Bad (2). They are historical labels, not observed lending approvals.
- The cost matrix assigns cost 5 to a Bad-labelled record predicted Good and cost 1 to a Good-labelled record predicted Bad.
- The age grouping is an exploratory analysis choice, not a legal category.
- Synthetic demo records are invented and must never be presented as observed evidence.
- The Health equity lab is reproducible synthetic data. It does not establish anything about real patients, tools, or health systems.
- UCI remains the app's only end-to-end predictive-model benchmark; it is historical and is not made current by re-downloading it. The **Mortgage application outcomes** page queries aggregate action counts from the CFPB/FFIEC HMDA Data Browser API for years 2018–2025. The 2025 browser view uses a snapshot frozen June 2, 2026; published data are privacy-modified and omit the underwriting context needed to explain decisions. These are observed mortgage filing patterns, not predictions or proof of discrimination.\n- The separate **Live consumer signals** page fetches recent aggregate complaint counts from the CFPB Consumer Complaint Database. The CFPB generally updates that source daily; FairLens caches results for up to one hour and offers a manual refresh. Complaints are not representative rates, verified violations, lending outcomes, or evidence about model fairness.

For claims, use the **Claim checker**, cite the source and analysis configuration, include group sizes and uncertainty, and distinguish observed differences from causal or legal conclusions.

## Hands-on tools

| Page | What you can do |
| --- | --- |
| **Applicant map** | Every applicant is a dot placed by similarity (PCA of non-sensitive inputs). Colour by score, group, mistakes or label; overlay a *fairness terrain* of look-alike regions where the two age groups are classified differently (blank where counts are too small); click a dot for a "why this score" chart, a look-alike check and a what-if path. |
| **Applicant simulator** | Build a fictional applicant with sliders. Live score, per-input contributions, shortest what-if chain, and a one-click comparison of original and changed-group predictions. Inputs follow the historical benchmark, including credit history, credit amount, installment rate, and age. |
| **Over-claim game** | Eight statements about audits: decide whether an audit like this can support each one, with an explanation after every round. |
| **Interface helpers** | Breadcrumb header with a "next in the route" link, HUD-style corner frames, staggered entrance and signal-line animations (all disabled under reduced-motion settings), quick-jump page finder in the sidebar, a guided audit-route list with a "Next" link, hover definitions for specialist terms, an interactive error-cost explorer on Home, an animated threshold sweep in the Health lab, light and dark themes, and a print-friendly layout for sharing findings. |
| **Hidden bias challenge** | Predict whether favorable classifications differ between age groups, then reveal validation-set rates, denominators, and 95% intervals. The challenge's 5-point comparison band is a game rule, not a fairness standard. |
| **Proxy detector** | Cross-validated test of whether age can be recovered from the other inputs, per-input proxy strength, and a with/without-age outcome comparison. |
| **Mitigation lab** | Baseline, cost-tuned threshold, input removal, reweighing and a group-threshold what-if on one cost-versus-gap map, with bootstrap intervals. |
| **Health lab (synthetic)** | A fully simulated screening scenario: change a threshold, a score shift and a prevalence to see how sensitivity gaps move. Invented data only; not clinical evidence or health advice. |
| **Claim checker** | Pick a common fairness claim (for example "the model is fair") and tick the evidence you actually have; the app shows what FairLens can and cannot support and what is still missing. Educational guidance, not a legal test. |
| **Audit your own model** | Upload any CSV of decisions or scores plus a group column; get rates with intervals, error rates if truth is supplied, and plain-language findings. |\n| **Mortgage application outcomes** | Explore HMDA application action counts by reported race, ethnicity, or sex, nationwide or by state. This is a descriptive pattern check, not model validation or a causal/legal finding. |\n| **Live consumer signals** | Review recent CFPB complaint totals by product category. Complaints are not a representative sample or verified findings. |

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


## Local AI Audit Guide

The FairLens chat sits at the lower-left of the main content area, clear of Streamlit's bottom-right controls, and offers page-specific starter questions about methods, metrics, aggregate results, uncertainty, and audit follow-up. It refuses personal financial, lending, health, legal, investment, and individual eligibility advice. Answers are educational and may be wrong; they are not financial advice.

The local AI is optional and uses WebLLM with the Qwen2.5 0.5B Instruct model through WebGPU. Its runtime and model files are first fetched only after a visitor clicks **Download local AI to enable Q&A**. That opt-in is remembered in this browser, so other app tabs can initialize their own local runtime from cached files. The initial download may take several minutes; the chat shows actual transfer progress when available and streams replies as they are generated. If browser storage is cleared, model files may need to be fetched again. Questions and chat history are stored only in this browser, not sent to the app server. **Clear chat** removes saved history across the open tabs. The guide receives curated FairLens facts about the dataset, labels, metrics, methods, and limits, plus the current page title and any allow-listed aggregate pinned-review summary. It does not receive page charts, applicant rows, uploaded files, or personal records.

A single search bar sits just below Streamlit’s top toolbar on every page. It finds and highlights matching terms on the page currently open, with controls to move between matches. The app has no sound effects.

Verify important interpretations against the displayed data, method notes, and cited sources.
