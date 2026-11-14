# Product principles

FairLens should feel like a careful guide through an investigation, not an intimidating monitoring console.

## Start with the human question

Every page begins with a plain-language question: What is in this dataset? What kinds of mistakes does the model make? Do those mistakes differ between groups? What changes if we adjust the decision rule? What can we responsibly conclude?

## Explain before adding complexity

Use plain-language summaries first. Technical definitions, equations, and implementation details can be available in expandable sections.

## Never detach a metric from its context

Show the metric definition, its numerator and denominator where meaningful, group sample count, evaluation split, and positive-class definition. A rate without its sample size is incomplete.

## Use a restrained visual system

Suggested palette:
- Warm paper: #F6F5F0
- Forest ink: #223B35
- Deep green: #315D50
- Muted green: #78948A
- Soft amber: #A87838
- Quiet border: #E4E4DC

Use color as reinforcement, never as the sole way to communicate meaning. Keep text contrast readable. Avoid decorative gauges, unexplained composite scores, and excessive animation.

## Separate evidence from interpretation

Label each statement as one of:
- **Observed:** directly present in the dataset.
- **Measured:** calculated from predictions and labels.
- **Interpretation:** a possible explanation that needs further evidence.
- **Limitation:** what the analysis cannot establish.

## Preserve human oversight

FairLens is a learning and review tool. It must not recommend approving or rejecting real applicants or imply that a threshold change automatically makes a system fair.
