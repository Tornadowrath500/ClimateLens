# Submission guide (Veritas AI Hackathon 2026)

Deadline per docs/PROJECT_CONTEXT.md: **Sunday, Nov 15, 2026, 11:59 PM Eastern**. Resubmission is allowed; the latest counts.

## Before you record or write anything
1. `python scripts/download_dataset.py` (or use the in-app button), then `python -m pytest`, then `streamlit run app.py`.
2. Click through all pages, run the 30-split stability check, pin one setting, and download the report from page 5.
3. Copy numbers **only** from the app or the downloaded report. Never from this repo's docs: none are recorded here.

## One-page write-up skeleton
- **Problem:** models can make different mistakes for different people; reviewers need a plain-language way to see that.
- **What we built:** FairLens, a guided five-step audit of a credit-risk classifier on the UCI German Credit data.
- **Method:** leakage-safe pipelines, class x age stratified 64/16/20 split, thresholds chosen on validation only, UCI 5:1 cost matrix, Wilson intervals, 30-split stability.
- **Findings:** paste the Observations from the report (baseline vs model cost, group rates with n, stability result).
- **Failure case:** paste one from the app, e.g. a validation-vs-test cost shift, a gap that changes sign across splits, or the per-group-threshold what-if.
- **Limitations:** from page 6. State plainly that gaps are not proof of discrimination.
- **Credits:** UCI dataset (CC BY 4.0), libraries, and AI tools used.

## 2-minute demo script
1. (10s) Home: what it is and is not.
2. (20s) Data: 1,000 records, label meaning, the 5:1 cost, the two age groups with their sizes.
3. (25s) Evaluate: baselines vs model; note what the cost matrix rewards; show the confusion matrix.
4. (30s) Group outcomes: intervals and denominators; run the 30 splits and say what it shows.
5. (25s) Experiment lab: drag the threshold, jump to the validation-best, pin it, compare validation vs test.
6. (10s) Findings: download the report; close on limitations.

## Checklist
- [ ] Repo public, README quick start works from a clean clone
- [ ] CI green; no data or secrets committed
- [ ] Write-up numbers match the report
- [ ] AI assistance disclosed per the competition rules
