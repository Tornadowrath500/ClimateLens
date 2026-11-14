# Roadmap

Evidence gates, not promises. [x] = implemented and unit-tested on synthetic data; **verify on the real UCI file** before claiming results.

## Milestone 0 - Reproducible foundation
- [x] Structure, conventions, CI workflow, explicit download (script and in-app button)
- [x] Target-label definitions, schema validation, provenance manifest check
- [ ] Run the download in a clean environment; record the real schema and manifest

## Milestone 1 - Baseline
- [x] All-Good baseline and All-Bad reference; UCI 5:1 cost matrix; data dictionary
- [x] Stratified train/validation/test split (class x age group)
- [ ] Reproduce baseline numbers on the real data and check against the UCI description

## Milestone 2 - Models
- [x] Logistic regression and random forest in leakage-safe pipelines; validation comparison
- [x] Keep the final test set hidden from exploratory pages; unlock one pinned review per app session
- [ ] Review instability and calibration on real data

## Milestone 3 - Group audit
- [x] Counts, rates, 95% Wilson intervals, repeated-split stability, age-removed check
- [ ] Extend to sex / foreign-worker groups

## Milestone 4 - Threshold experiment
- [x] Validation-only slider, cost curve, per-group what-if thresholds, one-time pinned test review
- [ ] Optional: Fairlearn ThresholdOptimizer for comparison

## Milestone 5 - Communication
- [x] Findings page and Markdown report generated from measured results
- [ ] One-page write-up and 2-minute demo (see docs/SUBMISSION.md)
