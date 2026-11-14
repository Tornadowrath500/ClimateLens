# Roadmap

This roadmap is a sequence of evidence gates, not a promise that every feature will be completed.

## Milestone 0 — Reproducible foundation

- [x] Repository structure and development conventions
- [x] Explicit UCI data-download script
- [x] Target-label definitions checked against UCI
- [x] Basic schema, baseline, and group-metric tests
- [ ] Run the download script in a clean environment
- [ ] Record the actual downloaded schema and manifest

**Exit condition:** another teammate can reproduce the dataset download and pass the starter tests.

## Milestone 1 — Establish the baseline

- [ ] Inspect feature names, value types, and target encoding
- [ ] Reproduce the all-Good baseline
- [ ] Calculate the UCI cost-matrix error cost
- [ ] Write a clear data dictionary
- [ ] Confirm stratified train/validation/test splits

**Exit condition:** a reproducible baseline report with no model-selection leakage.

## Milestone 2 — Compare candidate models

- [ ] Fit logistic regression and random forest pipelines
- [ ] Select model and preprocessing using validation data only
- [ ] Evaluate once on the untouched test set
- [ ] Report confusion matrices and class-specific metrics
- [ ] Investigate errors and instability

**Exit condition:** a model comparison that can be reproduced from source.

## Milestone 3 — Descriptive group audit

- [ ] Define the age grouping before inspecting favorable results
- [ ] Show group sample counts and target composition
- [ ] Calculate predicted-Good rates and class-specific error rates
- [ ] Add uncertainty intervals where appropriate
- [ ] Explain why differences do not establish causation

**Exit condition:** metrics are interpretable, supported by adequate sample sizes, and not presented as proof of discrimination.

## Milestone 4 — Threshold experiment

- [ ] Choose thresholds using validation data only
- [ ] Compare error trade-offs and the supplied cost matrix
- [ ] Show how group outcome measures change
- [ ] Preserve the untouched final test set

**Exit condition:** a transparent experiment with explicit trade-offs, not a claimed fairness fix.

## Milestone 5 — Mitigation and communication

- [ ] Test one documented mitigation method if justified
- [ ] Compare predictive performance and group outcomes before and after
- [ ] Include a failure case
- [ ] Produce a reproducible audit summary
- [ ] Complete accessibility, usability, and clean-install checks

**Exit condition:** an honest end-to-end demonstration and a concise explanation of what the evidence does and does not support.
