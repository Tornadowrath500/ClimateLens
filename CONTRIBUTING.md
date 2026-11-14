# Contributing to FairLens

Thank you for helping build FairLens. The project should be understandable, reproducible, and careful about claims.

## Before you start

1. Read the README and docs/DATA_AND_ETHICS.md.
2. Check existing issues and avoid duplicating work.
3. Ask before changing the target definition, age-group boundary, data source, or evaluation protocol.

## Branch and pull-request workflow

- Keep main runnable.
- Create a short-lived branch such as feature/model-baselines or feature/fairness-metrics.
- Keep changes focused.
- Open a pull request and describe what changed, why, and how it was tested.
- Do not select models or thresholds using final-test performance.

## Before requesting review

- Run python -m pytest.
- Check that no local data, credentials, or generated model artifacts were added.
- Add or update tests for changed behavior.
- Document metric definitions and denominators.
- Distinguish measured results from assumptions and interpretations.
- Include known limitations and a failure case where relevant.
- Credit datasets, libraries, references, and AI development tools used.

## AI-assisted development

AI coding assistants may be used as development tools, but contributors remain responsible for understanding, testing, and explaining submitted code. Do not paste secrets or private information into assistants. Record meaningful AI assistance and follow the competition's disclosure requirements.

## Respectful review

Critique methods and evidence, not people. Ask whether a result is reproducible and properly interpreted. Do not turn a group difference into an unsupported allegation.
