# Data, attribution, and responsible-use notes

## Dataset

**Statlog (German Credit Data)**  
Creator: Hans Hofmann  
Donated to UCI: November 16, 1994  
UCI dataset ID: 144  
DOI: https://doi.org/10.24432/C5NC77  
Source: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data  
Dataset license: CC BY 4.0

UCI describes 1,000 instances and 20 features. The target is class, with 1 = Good and 2 = Bad. The source includes a cost matrix in which predicting Good for an actually Bad case has cost 5, while predicting Bad for an actually Good case has cost 1. The rows of the source matrix are actual classes and columns are predicted classes.

## Important limitations

- The data were donated in 1994 and reflect a specific historical German context.
- The benchmark does not represent current lending practices, regulations, applicants, or economic conditions.
- Features and group labels are historical and may encode social assumptions of their time.
- The sample is small. Some group or intersectional comparisons may have very small denominators.
- The source labels are not a guarantee of a real applicant's future repayment behavior.
- An association between a feature and a prediction is not proof of causation.
- Unequal group metrics can motivate investigation; they do not independently establish discrimination or legal noncompliance.
- Fairness metrics express different values and can conflict. No single metric is a universal definition of fairness.

## Target and age definitions

The verified UCI encoding is:
- 1: Good credit risk
- 2: Bad credit risk

The dataset's age field is Attribute13. The initial exploratory grouping is under 25 versus 25 or older. This is a project analysis choice, not a legal threshold or a claim about protected-group status.

## Data handling

- Download data only by explicitly running python scripts/download_dataset.py.
- Keep the downloaded CSV and manifest local; data/raw/ is ignored by Git.
- Do not upload applicant-level rows, private data, or credentials to GitHub.
- If derived data are ever shared, re-check the source license and include attribution.

## Required project disclaimer

> This project is a prototype and is not financial advice.

The app and all submission materials must include this sentence.

## Repository software license

The benchmark's CC BY 4.0 license applies to the dataset, not automatically to FairLens code. The team has not yet selected a license for its own software. Agree among contributors before adding one.
