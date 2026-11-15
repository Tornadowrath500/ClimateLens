# Submission and demo writing guide

Use this as a preparation aid, not as a source of results. Confirm current competition requirements, dates, and word limits from the official organizer before submitting; this file intentionally avoids hard-coded deadlines.

## Before writing

1. Confirm the live Streamlit app is running the intended `main` commit.
2. Run the app and existing test suite. Record any check that was not run.
3. Follow the in-app route: Home → Data & scope → Model performance → Group outcomes → Claim checker → (optional) experiments → Findings & report.
4. If presenting the Health equity lab, state clearly that every record is synthetic and the outputs are illustrative only.
5. Copy numerical results from a fresh app run or downloaded report. Record model, data source, split, threshold/decision rule, and group sample sizes.
6. Read [Data and ethics](DATA_AND_ETHICS.md) and [Project context](PROJECT_CONTEXT.md).

## Suggested short narrative

- **Need:** Reviewers need a clear way to inspect a model's behavior, errors, and group outcomes.
- **What FairLens does:** It guides people through a historical credit-risk benchmark, performance and group analysis, threshold/input experiments, and evidence-aware reporting.
- **What makes it approachable:** Plain-language explanations, a guided dashboard, interactive comparisons, and a Claim checker that helps prevent overclaiming.
- **What the health-sector connection is:** The synthetic Health equity lab demonstrates how assumptions and thresholds can affect group metrics. It is a teaching illustration, not evidence about clinical tools or patients.
- **What was learned:** Insert only findings reproduced from the current app run. Explain the dataset and model conditions behind them.
- **Limits:** The main data are 1,000 German credit records collected in 1994; labels and coding have limitations; subgroup analyses can be uncertain. Results do not describe current applicants or prove causation, fairness, or discrimination.
- **Next step:** Explain what local, recent, appropriately governed data and expert review would be needed before applying the methods in another setting.

## Claim hygiene

Use bounded wording: “On this historical benchmark, under this evaluation setup, the model …” Avoid presenting an accuracy score as proof of fairness or treating a group gap as a legal conclusion. Do not write fabricated numbers, imply current data synchronization, or describe the synthetic health example as a real audit.

## Demo checklist

- [ ] Home opens first and communicates the product in under a minute.
- [ ] Select the correct data mode and label it accurately.
- [ ] Show at least one result with group counts and uncertainty.
- [ ] Explain the different costs assigned to the two error types.
- [ ] Use Claim checker to demonstrate the boundary between measurement and conclusion.
- [ ] Keep the health simulation separate from historical credit evidence.
- [ ] Download/inspect the report only after deliberately pinning the final test review.
- [ ] Verify the app URL, deployed commit, and official submission instructions immediately before the demo.
