"""Small, source-backed aggregates from the CFPB Consumer Complaint Database."""

from __future__ import annotations

from datetime import date
from typing import Any

import requests

CFPB_API_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"
CFPB_SOURCE_URL = "https://www.consumerfinance.gov/data-research/consumer-complaints/"


def parse_complaint_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize the aggregate fields used by the live-context page."""
    if not isinstance(payload, dict):
        raise ValueError("The CFPB response was not a JSON object.")

    hits = payload.get("hits")
    total = hits.get("total") if isinstance(hits, dict) else None
    if isinstance(total, dict):
        total = total.get("value")
    if not isinstance(total, int) or total < 0:
        raise ValueError("The CFPB response did not include a valid total count.")

    aggregations = payload.get("aggregations")
    product = aggregations.get("product") if isinstance(aggregations, dict) else None
    field = product.get("field") if isinstance(product, dict) else None
    buckets = field.get("buckets") if isinstance(field, dict) else None
    if not isinstance(buckets, list):
        raise ValueError("The CFPB response did not include product aggregates.")

    products = []
    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        label, count = bucket.get("key"), bucket.get("doc_count")
        if isinstance(label, str) and isinstance(count, int) and count >= 0:
            products.append({"product": label, "count": count})
    products.sort(key=lambda item: item["count"], reverse=True)

    meta = payload.get("_meta")
    meta = meta if isinstance(meta, dict) else {}
    return {
        "total": total,
        "products": products,
        "last_updated": meta.get("last_updated"),
        "last_indexed": meta.get("last_indexed"),
        "is_data_stale": bool(meta.get("is_data_stale", False)),
        "has_data_issue": bool(meta.get("has_data_issue", False)),
    }


def fetch_complaint_summary(start_date: date, end_date_exclusive: date) -> dict[str, Any]:
    """Fetch CFPB's date-filtered aggregate search result (no narratives or individual rows)."""
    if not isinstance(start_date, date) or not isinstance(end_date_exclusive, date):
        raise TypeError("Dates must be datetime.date values.")
    if start_date >= end_date_exclusive:
        raise ValueError("The end date must be later than the start date.")

    response = requests.get(
        CFPB_API_URL,
        params={
            "date_received_min": start_date.isoformat(),
            "date_received_max": end_date_exclusive.isoformat(),
            "size": 1,
            "no_aggs": "false",
        },
        headers={"Accept": "application/json"},
        timeout=20,
    )
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError as exc:
        raise ValueError("The CFPB returned a response that was not valid JSON.") from exc
    return parse_complaint_summary(payload)
