# Project Context & Continuity Handoff

> Temporary working document for future AI assistants, coding agents, and human teammates.  
> The team intends to delete this file after the project is complete. Until then, treat it as the main continuity brief and read it before proposing major changes.

**Last updated:** 2026-11-14  
**Repository:** `Tornadowrath500/ClimateLens`  
**Current product direction:** FairLens  
**Status:** Starter skeleton; not yet a validated, completed fairness-audit application.

---

## 1. What this project is

FairLens is an educational, human-centered model-auditing tool. Its purpose is to help a person understand how a predictive model behaves, what evidence supports its results, whether outcomes differ across groups, and what trade-offs follow from changing model choices.

The initial case study is a historical credit-risk classifier using the UCI Statlog (German Credit Data) benchmark.

**Product promise:** make model behavior and its limitations understandable to a human reviewer. Do not make consequential decisions for people.

FairLens is not:
- a real loan approval or credit-scoring service;
- a tool for evaluating actual applicants;
- proof that a model is fair or legally compliant;
- a generic AI chatbot or a wrapper around a paid LLM API;
- a system that reduces fairness to one overall score.

Use language such as **favorable prediction rate** or **Good-risk classification rate**, not “approval rate,” unless explicitly explaining that this is only a proxy label. The benchmark contains historical risk labels, not records of actual lender approval decisions.

## 2. Why this direction was chosen

The team is participating in the Veritas AI International High School Hackathon 2026. The goal is to produce a competitive, genuinely working submission, with an ambition to contend for Gold and the associated Arecibo AI internship. This is an ambition, not an outcome to promise.

The project direction was selected to balance:
- implementability within a short hackathon window;
- enough meaningful features to demonstrate depth;
- a clear, demonstrable user problem;
- measurable technical work rather than a superficial interface;
- room for improvement without making the first version unfinishable;
- responsible, transparent presentation of model outputs.

The user originally explored ClimateLens and asked to preserve its values, not necessarily its code or climate-specific subject matter. Those values are transparency, visible assumptions, evidence, clarity, and human-centered design. FairLens is the current project direction. Do not switch back to climate forecasting or another idea without discussing the trade-off with the user.

## 3. Competition context and practical constraints

The team has three members. The competition submission information supplied to the team states:
- the submission window closes **Sunday, November 15, 2026 at 11:59 PM Eastern (8:59 PM Pacific)**;
- one team member submits for the team and enters all members' information;
- submission includes an accessible GitHub repository or Colab and a one-page write-up;
- a two-minute demo video is optional but recommended;
- resubmissions are allowed, with the latest submission used;
- a simple, working project is preferable to an ambitious incomplete one;
- all project code must be written within the official competition window; check the official rules for treatment of any starter material or AI-generated files and disclose tools/contributions accurately.

The team should verify the official competition page and organizer instructions before relying on dates or procedural details:
- Competition page: https://climatelens-qltf.onrender.com/

The team's stated priority is strong execution and a compelling demonstration. Do not optimize for feature count at the expense of correctness, reproducibility, and a complete end-to-end story.

## 4. Dataset and evidence

Initial benchmark:
- **UCI Statlog (German Credit Data)**: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- 1,000 historical examples, 20 input features.
- Original target encoding: 1 = Good, 2 = Bad (confirm against the source and downloaded data in code).
- Historical data donated in 1994 from a German context.
- The source provides an asymmetric cost matrix: classifying an actually Bad-risk case as Good has five times the cost of the reverse error.

Important interpretation:
- This is a small, old, geographically and historically specific benchmark. It does not represent today's lending market or current applicant populations.
- The dataset does not contain actual lender approval decisions. A model prediction of Good risk is a favorable class prediction, not evidence that a real loan would have been approved.
- Do not imply the dataset establishes current discrimination or legal non-compliance.
- Group differences are descriptive evidence that may warrant investigation; they do not, by themselves, establish cause, intent, or discrimination.
- Small subgroup counts make estimates unstable. Always show group denominators and qualify conclusions.

Use the original UCI source as the authority for dataset details, target coding, and cost matrix. Cite it in project documentation and the final write-up. Do not invent dataset facts or model results.

## 5. Product principles and interaction design

The interface should feel calm, clear, approachable, and trustworthy—not like a dense technical dashboard.

Visual direction:
- warm off-white / neutral background;
- forest green or teal as restrained accent colors;
- muted sage and restrained amber for secondary states;
- readable typography, generous spacing, clear hierarchy;
- charts that explain one thing at a time.

Core experience: a guided journey, not a wall of charts:
1. **Understand the data** — source, target, feature types, class balance, missingness, and limitations.
2. **Evaluate the model** — baseline and candidate model performance on held-out data.
3. **Investigate group outcomes** — group definitions, sample sizes, rates, error patterns, and uncertainty.
4. **Experiment with changes** — threshold and, if properly implemented, mitigation trade-offs.
5. **Review findings** — concise audit summary with methods, evidence, and limitations.

Every important metric should answer:
- What does this measure?
- What is the denominator / sample size?
- What does a higher or lower value mean?
- What does it not tell us?
- How was it calculated?

Make methodology discoverable without overwhelming first-time users. Put a plain-language explanation first, with technical details available when needed. Do not rely on color alone to communicate risk or status.

Always distinguish:
- **Observed data** (what is in the dataset);
- **Model output** (what the model predicts);
- **Interpretation** (what a reviewer may cautiously infer);
- **Limitation** (what cannot be concluded).

## 6. Technical direction

Preferred stack for the current prototype:
- Python 3.11+
- Streamlit for the application;
- pandas and NumPy for data work;
- scikit-learn for preprocessing, baselines, and candidate models;
- Fairlearn for group metric analysis and, only if justified, mitigation experiments;
- Plotly for interactive charts;
- pytest for automated tests;
- ucimlrepo or a documented direct download for data acquisition.

No paid model API, cloud GPU, or LLM is required for the core product. Do not add an LLM just to make the project appear more “AI-powered.” The useful AI/ML work is the transparent, reproducible evaluation of actual predictive models.

Keep data acquisition explicit. Do not silently download or mutate datasets at app startup. Do not commit the raw benchmark data unless there is a clear, justified reason and the dataset terms have been checked. Keep local data out of Git and document its source.

Current repository layout (verify against the live tree before making assumptions):
- `app.py`: Streamlit landing / app entry point
- `pages/`: guided application pages
- `src/fairlens/`: data, schema, preprocessing, models, metrics, explanations, reporting
- `scripts/`: explicit dataset acquisition
- `tests/`: automated checks
- `docs/`: methodology, data/ethics, roadmap, design decisions
- `data/`: local-only data and manifest; not committed
- `requirements.txt`, `pyproject.toml`: dependencies and package configuration

Prefer small, testable modules and explicit interfaces over a monolithic Streamlit script. Keep UI code separate from model and metric logic.

## 7. Evaluation methodology — non-negotiable safeguards

This is a static tabular classification dataset, not a time series. A stratified random split is appropriate; do not apply climate-forecasting chronological split rules to this dataset.

Expected evaluation structure:
1. Inspect and validate raw data and target encoding.
2. Create stratified training, validation, and final test partitions (or a clearly justified equivalent).
3. Fit preprocessing only on training data, inside scikit-learn Pipelines to avoid leakage.
4. Use validation data for model/threshold selection.
5. Evaluate the selected approach once on the untouched final test set.
6. Make the split seed and proportions explicit and reproducible.
7. Compare against a simple baseline: predict every example as Good risk. With the source's 700 Good / 300 Bad distribution, this is about 70% accuracy but detects no Bad-risk cases; recompute from the actual loaded data rather than hard-coding.
8. Report class-specific metrics and confusion matrix, not accuracy alone.
9. Include the asymmetric error cost in the correct direction.

Cost interpretation when the positive class is encoded as Good:
- Actual Bad predicted Good = false positive for the Good class; this is the more costly error (cost 5).
- Actual Good predicted Bad = false negative for the Good class; this is the less costly error (cost 1).
Confirm the mapping in code and tests. Never assume the positive class without explicitly setting it.

Useful metrics may include accuracy, balanced accuracy, precision, recall, F1, confusion matrix, and precision-recall AUC where suitable. Explain the choice and the class of interest. Avoid accuracy-only claims on imbalanced data.

For age-group analysis, the competition brief specifically suggests comparing **under 25** with **25 or older**. Define the groups explicitly, show counts, and calculate group metrics on the same evaluation population. Be careful with alignment between feature rows, labels, predictions, and group labels.

Do not:
- fit preprocessing on the full dataset before splitting;
- tune thresholds on the final test set;
- select features using test labels;
- report training scores as test performance;
- hard-code expected metric values;
- hide small denominators;
- interpret feature importance as causation;
- claim that equal favorable prediction rates alone prove fairness.

## 8. Planned feature sequence

Build in this order. Reassess scope based on time remaining.

### Phase 1 — prove the core works
- reliable dataset loading and schema validation;
- reproducible stratified split;
- baseline prediction;
- Logistic Regression pipeline;
- core evaluation metrics and confusion matrix;
- clear data and methods pages;
- tests for target mapping, split behavior, metric calculations, and leakage-sensitive preprocessing.

### Phase 2 — make the fairness investigation meaningful
- under-25 vs 25+ group definitions;
- favorable prediction rates and group denominators;
- group-specific false-positive / false-negative rates and other justified metrics;
- plain-language explanations and careful caveats;
- uncertainty estimates if feasible and correctly implemented.

### Phase 3 — interactive investigation
- validation-selected global threshold slider;
- update favorable prediction rate, error rates, and dataset cost as threshold changes;
- compare threshold settings on the same population;
- clearly label the threshold experiment as a trade-off, not a fairness fix.

### Phase 4 — extensions only after validation
- Random Forest as a challenger model;
- feature inspection / permutation importance with explicit caveat that association is not causation;
- one controlled mitigation experiment, if it can be implemented and evaluated fairly;
- downloadable audit report with dataset citation, split, models, metrics, group counts, assumptions, and limitations.

A mitigation experiment must show both fairness-related metrics and predictive-performance / cost trade-offs. Do not silently apply different thresholds to protected groups or call a technique a guaranteed fix. If there is not enough time to validate a mitigation, leave it out and explain why.

## 9. Current status — do not overstate

The repository has been initialized as a FairLens starter skeleton. The README describes the intended product, methodology commitments, layout, and setup.

The prior handoff reported an initial scaffold commit and subsequent fixes. The currently verified repository README states that this is still a **starter skeleton** and that trained models, measured results, and a completed fairness audit are not yet present.

Therefore, unless independently verified by running code and inspecting the live repository:
- do not say the models are trained;
- do not quote performance or fairness numbers;
- do not claim the full app or all pages work end to end;
- do not claim tests pass merely because test files exist;
- do not assume a previous assistant's claimed commit/test status is accurate.

First actions for a future coding agent:
1. Inspect the actual GitHub tree and recent commits.
2. Read README and all docs before editing.
3. Create a clean local environment and install dependencies.
4. Run the existing tests and app; record failures honestly.
5. Fetch the dataset explicitly and verify columns, target encoding, and row count.
6. Fix the smallest blocking issue and add a regression test.
7. Produce reproducible baseline results before adding more features.

## 10. Team and collaboration

There are three team members. Suggested division (adjust to real skills and availability):
- **Data / evaluation owner:** dataset integrity, preprocessing, baselines, models, metric correctness.
- **Fairness / methodology owner:** group definitions, fairness metrics, interpretation, uncertainty, mitigation experiment.
- **Product / demo owner:** Streamlit experience, usability, visual hierarchy, report, demo narrative.

This is a suggested division, not a claim about assigned roles. All members should make genuine contributions and understand the full project well enough to answer questions. Keep a record of who contributed what and disclose AI-assisted work according to competition rules.

The user prefers Claude as a coding assistant when available, but tool/account access and age requirements may constrain choices. Do not recommend circumventing service age restrictions. Any coding assistant should be given this file and asked to inspect the live repository before modifying it.

## 11. Instructions for future AI / coding agents

Before coding:
- Read this document, README, methodology docs, and relevant tests.
- Inspect the current repository rather than trusting this handoff as a live inventory.
- State what exists, what is broken, and what you plan to change.
- Prefer a small working increment over a broad rewrite.
- Ask before changing the product direction, dataset, target definition, or core methodology.

While coding:
- Do not fabricate results, citations, test output, or completion claims.
- Do not silently change target encoding, group definitions, split strategy, or metric definitions.
- Keep model logic out of UI modules.
- Add tests for every important calculation and bug fix.
- Use explicit random seeds and reproducible preprocessing.
- Keep dependencies lean; avoid paid APIs and unnecessary infrastructure.
- Preserve the transparent, human-centered design.
- Explain meaningful assumptions and limitations in the UI and docs.

When reporting back:
- List exact files changed.
- State commands actually run and their real outcomes.
- Separate implemented, tested, and not-yet-tested work.
- Include known limitations and the next smallest useful milestone.
- Never imply that a feature is complete merely because a page or placeholder exists.

## 12. Definition of a credible first demo

A credible first demo should be able to:
1. Explain what the dataset is and why it is limited.
2. Show its class distribution and target meaning.
3. Run the simple baseline and at least one properly pipelined model.
4. Display held-out test metrics and a confusion matrix.
5. Explain the costlier error correctly.
6. Compare the specified age groups with visible denominators, without overclaiming.
7. Explain what a user can and cannot conclude.
8. Run reproducibly from the README instructions.

If any of these are not implemented, state that honestly and narrow the demo rather than faking the missing functionality.

## 13. Useful source links

- Competition information: https://climatelens-qltf.onrender.com/
- UCI Statlog German Credit dataset: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- scikit-learn Pipeline documentation: https://scikit-learn.org/stable/modules/compose.html
- Fairlearn documentation: https://fairlearn.org/
- Streamlit documentation: https://docs.streamlit.io/


## 14. Resources supplied by the user — preserve and consult

This section inventories project-related materials the user supplied in the ChatGPT conversation or linked during project planning. These are reference materials, not all active requirements. Prefer the original source when facts conflict; verify current competition rules rather than treating an old summary as authoritative.

### 14.1 Veritas AI hackathon organizer email

**User-supplied attachment:** `Pasted markdown(5).md` (organizer email, uploaded November 14, 2026).

The email supplied the following resources and instructions:
- Four available tracks: AI + Health, AI + Finance, AI + Climate, AI + Languages.
- Teams may use any public dataset if it is credited.
- Submission requires code in a shareable GitHub repository or Google Colab, a one-page write-up, and an optional but recommended demo video up to two minutes.
- One person submits for the whole team; the form collects every member's name, email, and school.
- Draft submission and resubmission are allowed; the latest version is used.
- The email emphasizes that a simple working project is better than an ambitious incomplete one.
- Contact listed in the email: contact@veritasai.com.

Organizer email links (HubSpot-tracked links copied from the supplied email; if a redirect expires, use the attached copies where available or ask the organizer):
- **Project briefs:** [Veritas AI Hackathon 2026: Project Briefs](https://d12LkD04.na1.hubspotlinks.com/Ctc/5E+113/d12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfHP5nXHCW50kH_H6lZ3kBW67Btq22-S5NKV46PPT8VJkJxW1C7lC68bJ8-cW675LvT2Nrr0vW8TJmW0348PMjW1-2Py93scFbxW4nd-Z83pFQFVW6QkQP24g9nCkW3nQltG5-lvfcW32CCmY5YbRSSW99jbcg5N5mMwW7Mn-LK4HLrXMN5G1fFYSVdZhW2qqwNf9cf0XTW3fK4Dy1j0xY_W9gC3f44qtg9hW5vh2Hy2WwK0mW1n0W1q56xZgXW5571M_4V4PllW2GH5pj1G67nnMn8H5ytBXwYW2hbmSm634-6nW7pm-g-6H4XCcW8HsDWv9l6MJ0W6D5mLf2gD2SvW6JRy8S4VvH5jW6mYhSW5DsMpXW7zy8LL8LQ01WW9fz7Sb73ylkgW1P8r9S1JxDm0W56rjmg1nM54kVQfvsZ3vWWCDf4-sydH04)
- **Sample submission:** [ScamCheck sample project](https://d12LkD04.na1.hubspotlinks.com/Ctc/5E+113/d12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfHP5nXHCW50kH_H6lZ3nSW3bB4bb6zttnFW7-hykZ5M-GRgW6v_pBQ5QhkJpW7dTKXC73wS_qN5_5x0YSNcQwW1BXtc-3HwvQKW7cnVj55X91l7W4k214_97WK-6W97r9sL6w87zvW3Y_QrV7rSBH-W3fJCSZ7l8_5lW7WcL511JdyR7N7LBpNc78-MxW8KFV0k5YfG75W58v9ms6GsDN6W2jQ1X92vb9J0W1xMqtV7kF7q9W1-rh5h8v8LLnW8GGfyz5j-ThFVRkQd33DfYpwW7vzsc-5NCnYDW7YCJ3w8cbHy1W1VdRz61g2M9tW7-0YGx5WlK5vW61xmbj1vb467W8N0sFG58BnltW50SjFx4VyQFJW7CnM0g5htbhPN3K5lWZNF8pfVlJQpJ63Kf_8W4z6PRs7tPnLVW3Nj7pq590NW3f5mgSxH04)
- **Submission form:** [Veritas AI submission form](https://d12LkD04.na1.hubspotlinks.com/Ctc/5E+113/d12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfKT3qn9qW95jsWP6lZ3n6N1kwcSxqWTTYW5VS3Y264cDTjW5WpFpW4WNdXtW7C2c-87lBjgsW5PcJTz4RcK8qW2pLm0M3yLw9jVCgdJ_6qJ175W6L5_MP86MjFLW6jQqGk86KJ-WW7RSJZj6d_r75W6YrX4m17-_7LW2Q83yM4nPyfZW304Dfb3L980SW8MmdHz8x5LstW1PWB3q22jZ2XW7jxFwg2bkb1HW3slyNM3pG_x8W70NKK92NnJg7MMX8PrQn68YW9ffZx91PtH6HW9lQdyg70Dv3zW3_2Qc499rHf3W7-W8j12TZ3fCW2nTsK48p7PGmVYFvSL7jX7TnW83FGrg8y7B9vW2jYLmZ43DhGrN1LhpH04hktzW6qDphN5CbVL8W2tSWVs7gfgV1f1stCyP04)
- **Hacker Guide:** [Rules, tools, and write-up template](https://d12LkD04.na1.hubspotlinks.com/Ctc/5E+113/d12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfHP5nXHCW50kH_H6lZ3mqMyXQXVpjQ3rW8pfHv39csD5nW5vzpYG4BNGVfW8_Lh7h2kv__VW5QK-Qm7L0rFPW57rRRm7WWbylW8q9bkH6ZwtqfW92WDH43wX4V9W3zr1PG7Ncv2PW11mv9M5_B8DXN8zMHm3L7YMwV2ynVW5rHjQFN1T1C6PZJMZtW7Kz6xW4rHBx4W4HT0SD2S79FxW5r2gW780KdVsN8l2SpHLJHdfW2B0FHF7-CHMRW1krr-l1cMdMsW7qSjmG4dwRkcW1fktQc3f2-8WW6sFvkS4VlhYTVhTZcF8fdKqfW87b1KR8f1ZlQV9zHll3kJHtmW1b2gDt6hDd6ZW66BKkB51C2X5W6FHF7K6l-w5SW7pQqNy3XlzT0W55KbF27kRZmPW4fyGkV9cMBjCW2KCPSG1MWw-Rf4GdmZ204)
- **Optional starter notebook:** [Google Colab / first AI model guide](https://d12LkD04.na1.hubspotlinks.com/Ctc/5E+113/d12LkD04/VX7YSq2pD7crW6T0H9r4McZ50W33LWhB5Xl1mmN4bXfJ45nXHCW5BWr2F6lZ3n-W98vB7d5qK19qW36szgz1D5JzsW2yVkLY4mR7GtW61nW_p8THHdRW5pM4TV5RcvVsW4yHDNp5Kq7ktW34YF_R8MXfZdVwyvx01C2lLmW6lht1x6ncvMnW4tDnWK6bJD1KW42ctq731mq75W2Fktsn3ttqDtW8lYYz05YgcPsW4RHhKm298-R0W3LMtzQ6928P2W4bb9Bs7qkFxgW2-rKYM1yYwKJVxydqz5zgkB1W4QqxlB8NJWYMW80CcnH30t5HLW4tX9779bWyGWW4bzqx03BkNhvW1ZKr2_6DMw5rW5vnWfb39_BwFW59jTkJ1wYVqVW8-mc7C3GCMV-W68RSgg41q3RmN3W0W8b6T-FFN1ttZdW8V7KyW6zH5TP9cM_jRW9g4bxp1S5pqFW4mhMMV42LdMkW9bbHX37gfKjXW8yMjPK59hRMPf2K_NZF04)

### 14.2 Competition files attached by the user

The user supplied two ZIP archives on November 14, 2026:

**`drive-download-20261114T070539Z-1-001.zip`**
- `Veritas AI International High School Hackathon 2026 Project Briefs.pdf`
- `Sample Submission ScamCheck, a scam text filter for grandparents.pdf`
- `ScamCheck_Sample_Submission (1).ipynb`

**`drive-download-20261114T070025Z-1-001.zip`**
- `Sample Submission ScamCheck, a scam text filter for grandparents.pdf`
- `ScamCheck_Sample_Submission (1).ipynb`

Use the project briefs as the competition's track-specific project guidance. The user and assistant reviewed the AI + Finance brief in particular. It discusses scam-message classification, card-fraud detection, a fairness audit of a credit model, and headline/sentiment analysis. The fairness-audit suggestion uses the UCI German Credit benchmark and specifically encourages checking age-group differences and proxy features. The brief emphasizes comparison to a simple baseline, appropriate metrics, dated/chronological splits where data has time, and honest limitations. For this FairLens project, follow the fairness-audit guidance and use a stratified split because the selected German Credit data is static, not time-series data.

The sample ScamCheck PDF and notebook are examples of the expected scope / presentation style, not source code or requirements to copy. Inspect them when useful for demo/write-up structure; do not copy their project wholesale.

### 14.3 ClimateLens source archives supplied by the user

The user also supplied several ZIP snapshots of the earlier ClimateLens project. These are historical reference material, not the current FairLens source of truth:
- `climatelens-main.zip`
- `climatelens-updated.zip`
- `ClimateLens-upgraded.zip`
- An earlier conversation also included the ClimateLens repository URL: https://github.com/ThienBao099/climatelens

The archives contain a Python backend, frontend, data ingestion/preprocessing, model training/prediction, climate indices, recommendations, tests, deployment configuration, and in later snapshots documentation such as `TEAM_STRATEGY.md`, `CODING_ASSISTANT_PROMPT.md`, `SUBMISSION_DRAFT.md`, `CHANGES_MADE.md`, and `REVIEW_AND_ROADMAP.md`. Some snapshots include generated model artifacts, processed data, training logs, and Python cache files. Treat those as historical project state, not validated current FairLens implementation. Do not transplant old ClimateLens code into FairLens without a deliberate review and explicit reason; the user asked for a blank-slate project skeleton and to retain the values rather than the old implementation.

The current working repository is:
- https://github.com/Tornadowrath500/ClimateLens

### 14.4 Public technical resources relevant to FairLens

These were shared or selected during project planning:
- **UCI Statlog (German Credit Data):** https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- **scikit-learn Pipeline / composition:** https://scikit-learn.org/stable/modules/compose.html
- **Fairlearn:** https://fairlearn.org/
- **Streamlit documentation:** https://docs.streamlit.io/

Use official documentation for current API behavior. Do not assume remembered code examples match installed versions.

### 14.5 How to use this resource inventory

- The ZIPs were supplied to ChatGPT; they are not automatically present in this GitHub repository. A future agent should ask the user to provide an archive again if the actual bytes are needed and not otherwise available.
- The original email contains HubSpot redirect URLs. If any stop working, prefer the attached local brief/sample files or ask the user for a fresh link; do not invent replacement URLs.
- The user supplied the resources for this hackathon/project context. Do not mistake unrelated school files or other unrelated conversation uploads for FairLens project resources.
- Do not treat every historic ClimateLens archive as current project code. FairLens and its new skeleton are the current direction.


---

**North star:** FairLens should help a person see what a model is doing, what evidence supports that understanding, where uncertainty remains, and what trade-offs follow from changing it. A smaller, correct, explainable project is stronger than a larger project that overstates what it knows.
