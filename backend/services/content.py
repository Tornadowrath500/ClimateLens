"""Plain-language metric explanations served to the frontend (kept beside the metrics they describe)."""

METRIC_HELP = {
    "accuracy": "Share of all applicants the model labelled correctly. Misleading when errors cost different amounts.",
    "recall_good": "Of applicants whose label is Good, the share the model also called Good. High means few good-risk people are turned away.",
    "recall_bad": "Of applicants whose label is Bad, the share the model correctly called Bad. This is how many risky cases it catches.",
    "precision_good": "Of applicants the model called Good, the share who really are labelled Good. Low means many 'Good' calls are mistakes.",
    "f1": "A single balance of precision and recall for the Good class. It ignores the 5-to-1 cost, so read it alongside cost.",
    "cost": "Average UCI cost per applicant: 5 for each Bad case called Good, 1 for each Good case called Bad. Lower is better.",
    "auc": "How well the model ranks Good above Bad cases regardless of threshold. 0.5 is a coin flip, 1.0 is perfect ranking.",
}

DEMO_NOTICE = (
    "Invented records with the German Credit layout, for exploring the tools offline. Not real evidence; "
    "download the real benchmark on the data page for genuine results."
)
DEMO_REPORT_HEADER = "> **SYNTHETIC DEMO DATA: invented records, not real evidence.**\n\n"