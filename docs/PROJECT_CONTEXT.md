# FairLens project context

**Purpose:** Working continuity brief for contributors and future writing.  
**Repository:** `Tornadowrath500/FairLens`  
**Live app:** https://fairlensinsight.streamlit.app/  
**Production entry point:** root `app.py` (Streamlit).  
**Current product:** educational model audit centered on a historical credit benchmark, with a separately labeled synthetic health-equity exploration lab.

## Product in one paragraph

FairLens helps a broad audience inspect how a predictive model behaves, compare errors and group outcomes, explore the effects of threshold or input changes, and communicate what the evidence can and cannot support. The app is designed to teach auditing concepts, not to make decisions about real people.

## Audience and presentation

Primary audience includes hackathon judges and learners who may not be financial analysts or machine-learning specialists. Lead with the question and practical meaning, define specialist terms in plain language, keep the first-run route clear, and show the limitations beside the results. The current Home dashboard is the intended first screen. Profile setup is optional.

## Current feature inventory

- **Home dashboard:** source-aware snapshot and guided path into the audit.
- **Data & scope:** benchmark, labels, data dictionary, provenance, and known limitations.
- **Model performance:** predictive metrics, baselines, error types, and cost-sensitive comparison.
- **Group outcomes:** descriptive rates, group counts, uncertainty, and stability exploration.
- **Applicant map and simulator:** inspect fictional or benchmark records and what-if profiles.
- **Experiment and mitigation labs:** explore threshold and input changes and the resulting trade-offs.
- **Proxy detector:** inspect whether other features carry information associated with a removed attribute.
- **Audit your model:** evaluate a user-provided model through the app's supported input contract.
- **Findings & report:** report on a deliberately pinned held-out test review.
- **Claim checker:** distinguish a measured result from stronger claims that need more evidence.
- **Health equity lab:** deterministic hypothetical records; only demonstrates how assumptions affect metrics.

Always verify current page code and tests before stating a feature works or is complete. Streamlit is the app users see; `frontend/` and `backend/` are separate prototypes and are not launched by `app.py`.

## Data, metrics, and limits

The main benchmark is the UCI Statlog (German Credit Data), UCI ID 144. It contains 1,000 historical German records collected in 1994. The app uses target values 1=Good and 2=Bad. They are labels, not approvals or direct measures of a lender's decision. The associated cost matrix is 5 for predicting Good on a Bad-labelled record and 1 for predicting Bad on a Good-labelled record.

The benchmark is small, historical, geographically specific, and has known errors/limitations in its coding documentation. The app's under-25 versus 25-and-over comparison is exploratory and must not be presented as a legal classification. Group metrics can be unstable, especially for smaller groups. Report denominators and uncertainty; do not infer causation or discrimination from a gap alone.

Synthetic demo and Health equity lab values are invented. Never describe them as real measurements. The health lab is not a clinical audit, medical advice, or evidence about patients or health systems. No live patient or current applicant feeds are integrated. A refreshed copy of the historical UCI benchmark is still historical.

## Responsible language

Prefer:
- “In this dataset, this model produced …”
- “The measured gap is … for these groups, with these sample sizes and uncertainty.”
- “This is a signal for further investigation.”
- “The simulation illustrates how the stated assumptions affect the result.”

Avoid unsupported claims such as “the model is fair,” “the model discriminates,” “removing age fixes bias,” or “this predicts current lending/health outcomes.” Separate descriptive results, causal claims, legal conclusions, and recommendations.

## Writing and judging checklist

For any presentation, submission, or demo:
1. State the problem as making model behavior understandable and reviewable.
2. Identify the actual data source, vintage, labels, model, and evaluation split.
3. Use numbers from a fresh run of the app or its downloaded report, not remembered or invented values.
4. Explain the trade-off shown and who may bear each type of error.
5. Mention small sample size, historical context, label quality, and uncertainty.
6. State what the analysis cannot establish and what local validation would be needed.
7. Keep synthetic health examples explicitly separate from credit benchmark evidence.
8. Verify the live deployment and repository commit before claiming a feature is live.

## Architecture and deployment

Streamlit Cloud should point to `Tornadowrath500/FairLens`, branch `main`, file `app.py`. `app.py` builds navigation from `pages/`. Shared UI and data/evaluation helpers live in `src/fairlens/`. GitHub Actions workflow `.github/workflows/tests.yml` runs checks; it does not itself deploy Streamlit. Verify the Streamlit deployment in its own settings/logs.

## Open work

See [Roadmap](ROADMAP.md) for known work. Treat checked items as verified only when the current implementation and checks support that status. Do not treat this brief as a substitute for reading the relevant source, data documentation, or test results.
