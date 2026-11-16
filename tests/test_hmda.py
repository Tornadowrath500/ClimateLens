import pytest

from fairlens.hmda import HMDA_API_BASE, fetch_hmda_aggregations, parse_hmda_aggregations

PAYLOAD = {
    "aggregations": [
        {"count": 80, "sum": 12000000, "actions_taken": "1", "races": "White"},
        {"count": 10, "sum": 1000000, "actions_taken": "3", "races": "White"},
        {"count": 35, "sum": 4500000, "actions_taken": "1", "races": "Black or African American"},
    ],
    "servedFrom": "cache",
}


def test_parse_hmda_aggregations_keeps_group_action_counts():
    result = parse_hmda_aggregations(PAYLOAD, "races")

    assert result["served_from"] == "cache"
    assert result["rows"] == [
        {"group": "White", "action": "1", "count": 80},
        {"group": "White", "action": "3", "count": 10},
        {"group": "Black or African American", "action": "1", "count": 35},
    ]


def test_parse_hmda_aggregations_rejects_error_response():
    with pytest.raises(ValueError, match="Invalid year"):
        parse_hmda_aggregations({"errorType": "bad-query", "message": "Invalid year"}, "races")


def test_fetch_hmda_aggregations_builds_bounded_aggregate_request(monkeypatch):
    import fairlens.hmda as hmda

    seen = {}

    class Response:
        def raise_for_status(self):
            pass

        def json(self):
            return PAYLOAD

    def fake_get(url, **kwargs):
        seen["url"] = url
        seen.update(kwargs)
        return Response()

    monkeypatch.setattr(hmda.requests, "get", fake_get)
    result = fetch_hmda_aggregations(2025, "Race", "CA")

    assert result["rows"][0]["group"] == "White"
    assert seen["url"] == HMDA_API_BASE + "/view/aggregations"
    assert seen["params"]["years"] == "2025"
    assert seen["params"]["actions_taken"] == "1,2,3,4,5"
    assert seen["params"]["states"] == "CA"
    assert "Black or African American" in seen["params"]["races"]
    assert seen["timeout"] == 45


def test_fetch_hmda_aggregations_rejects_invalid_grouping():
    with pytest.raises(ValueError, match="Race, Ethnicity, or Sex"):
        fetch_hmda_aggregations(2025, "Income", None)
