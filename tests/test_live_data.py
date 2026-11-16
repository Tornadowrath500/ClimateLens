from datetime import date

import pytest

from fairlens.live_data import CFPB_API_URL, fetch_complaint_summary, parse_complaint_summary


def sample_payload():
    return {
        "hits": {"total": {"value": 14}},
        "aggregations": {
            "product": {
                "product": {
                    "buckets": [
                        {"key": "Credit card", "doc_count": 9},
                        {"key": "Checking account", "doc_count": 5},
                    ]
                }
            }
        },
        "_meta": {
            "last_updated": "2026-11-14T00:00:00Z",
            "last_indexed": "2026-11-15T00:00:00Z",
            "is_data_stale": False,
            "has_data_issue": False,
        },
    }


def test_parse_complaint_summary_normalizes_and_sorts_counts():
    result = parse_complaint_summary(sample_payload())

    assert result["total"] == 14
    assert result["products"] == [
        {"product": "Credit card", "count": 9},
        {"product": "Checking account", "count": 5},
    ]
    assert result["last_indexed"] == "2026-11-15T00:00:00Z"
    assert result["is_data_stale"] is False



def test_parse_complaint_summary_accepts_published_schema_shape():
    payload = sample_payload()
    product = payload["aggregations"]["product"]
    product["field"] = product.pop("product")

    result = parse_complaint_summary(payload)

    assert result["products"][0] == {"product": "Credit card", "count": 9}


def test_parse_complaint_summary_rejects_missing_aggregates():
    with pytest.raises(ValueError, match="product aggregates"):
        parse_complaint_summary({"hits": {"total": {"value": 0}}})


def test_fetch_complaint_summary_uses_bounded_official_query(monkeypatch):
    import fairlens.live_data as live_data

    seen = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return sample_payload()

    def fake_get(url, **kwargs):
        seen["url"] = url
        seen.update(kwargs)
        return Response()

    monkeypatch.setattr(live_data.requests, "get", fake_get)
    result = fetch_complaint_summary(date(2026, 1, 1), date(2026, 1, 2))

    assert result["total"] == 14
    assert seen["url"] == CFPB_API_URL
    assert seen["params"] == {
        "date_received_min": "2026-01-01",
        "date_received_max": "2026-01-02",
        "size": 1,
        "no_aggs": "false",
    }
    assert seen["timeout"] == 20


def test_fetch_complaint_summary_rejects_empty_date_window():
    with pytest.raises(ValueError, match="end date"):
        fetch_complaint_summary(date(2026, 1, 2), date(2026, 1, 2))
