# Roadmap

This roadmap separates shipped capabilities from work that still needs evidence. A feature being present in the UI does not by itself validate its results.

## Current product

- [x] Streamlit app with guided navigation and Home dashboard.
- [x] Historical UCI credit benchmark workflow, data dictionary, provenance, and limitations.
- [x] Model performance and cost-sensitive evaluation.
- [x] Descriptive group outcome comparisons and uncertainty tools.
- [x] Applicant map/simulator, proxy exploration, threshold experiments, and mitigation tools.
- [x] Pinned held-out review and downloadable report.
- [x] Claim checker for evidence boundaries.
- [x] Clearly labeled deterministic synthetic Health equity lab.
- [x] Optional profile and guided tour.

## High-priority follow-up

- [ ] Verify every page end-to-end on the currently deployed Streamlit version and record the deployed commit.
- [ ] Add automated smoke coverage for navigation and the Claim checker / Health equity lab page rendering.
- [ ] Verify color contrast, keyboard navigation, mobile layouts, and screen-reader labels in both appearance modes.
- [ ] Reconcile the README, data ethics page, submission guide, and app wording after future feature changes.
- [ ] Confirm the app's Python version and dependency resolution are consistent between local, CI, and Streamlit Cloud.
- [ ] Review model upload constraints and make file-size/type/column expectations explicit at point of use.

## Research and product boundaries

- Do not imply the historical UCI dataset is current or representative of present-day applicants.
- Do not add a “live data” label unless an authoritative, maintained source is actually integrated and its freshness is shown.
- Do not infer a health claim from the synthetic lab. Real health use would require governed data, local validation, clinical/community input, privacy review, and separate risk assessment.
- Keep the user journey simple for non-specialist reviewers; add pages only when they clarify evidence or improve a real task.

## Definition of done

A change is done when the production Streamlit path uses it, its wording is accurate, it works on small screens and in both themes, relevant checks pass, and documentation describes the behavior that actually shipped.
