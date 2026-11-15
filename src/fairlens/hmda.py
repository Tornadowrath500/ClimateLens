"""Aggregate HMDA application outcomes from the FFIEC/CFPB Data Browser API."""

from __future__ import annotations

from typing import Any

import requests

HMDA_API_BASE = "https://ffiec.cfpb.gov/v2/data-browser-api"
HMDA_SOURCE_URL = "https://ffiec.cfpb.gov/data-browser/"
HMDA_DATASET_URL = "https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset"
HMDA_API_DOCS_URL = "https://ffiec.cfpb.gov/documentation/api/data-browser/"

HMDA_GROUPS = {
    "Race": {
        "parameter": "races",
        "values": (
            "American Indian or Alaska Native",
            "Asian",
            "Black or African American",
            "Native Hawaiian or Other Pacific Islander",
            "White",
            "2 or more minority races",
            "Joint",
            "Free Form Text Only",
            "Race Not Available",
        ),
    },
    "Ethnicity": {
        "parameter": "ethnicities",
        "values": (
            "Hispanic or Latino",
            "Not Hispanic or Latino",
            "Joint",
            "Ethnicity Not Available",
            "Free Form Text Only",
        ),
    },
    "Sex": {
        "parameter": "sexes",
        "values": ("Female", "Male", "Joint", "Sex Not Available"),
    },
}

HMDA_ACTIONS = {
    "1": "Loan originated",
    "2": "Approved, not accepted",
    "3": "Application denied",
    "4": "Withdrawn by applicant",
    "5": "Closed for incompleteness",
}


def parse_hmda_aggregations(payload: dict[str, Any], group_field: str) -> dict[str, Any]:
    """Validate an aggregate-only response and keep the fields needed for group comparisons."""
    if not isinstance(payload, dict):
        raise ValueError("The HMDA response was not a JSON object.")
    if isinstance(payload.get("errorType"), str):
        raise ValueError(str(payload.get("message") or "The HMDA API rejected this query."))

    aggregations = payload.get("aggregations")
    if not isinstance(aggregations, list):
        raise ValueError("The HMDA response did not include an aggregation list.")

    rows = []
    for item in aggregations:
        if not isinstance(item, dict):
            continue
        group = item.get(group_field)
        action = str(item.get("actions_taken", ""))
        count = item.get("count")
        if isinstance(group, str) and action in HMDA_ACTIONS:
            try:
                count = int(count)
            except (TypeError, ValueError):
                continue
            if count >= 0:
                rows.append({"group": group, "action": action, "count": count})
    return {
        "rows": rows,
        "served_from": payload.get("servedFrom"),
    }


def fetch_hmda_aggregations(year: int, group_by: str, state: str | None = None) -> dict[str, Any]:
    """Request public aggregate counts for action codes 1–5, never loan-level rows."""
    if year not in range(2018, 2026):
        raise ValueError("HMDA data year must be between 2018 and 2025.")
    if group_by not in HMDA_GROUPS:
        raise ValueError("Choose Race, Ethnicity, or Sex.")
    if state is not None and (len(state) != 2 or not state.isalpha() or state.upper() != state):
        raise ValueError("State must be a two-letter uppercase abbreviation.")

    group = HMDA_GROUPS[group_by]
    endpoint = "/view/nationwide/aggregations" if state is None else "/view/aggregations"
    params = {
        "years": str(year),
        "actions_taken": "1,2,3,4,5",
        group["parameter"]: ",".join(group["values"]),
    }
    if state is not None:
        params["states"] = state

    response = requests.get(
        HMDA_API_BASE + endpoint,
        params=params,
        headers={"Accept": "application/json"},
        timeout=45,
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError as exc:
        raise ValueError("The HMDA API returned invalid JSON.") from exc
    return parse_hmda_aggregations(payload, group["parameter"])
