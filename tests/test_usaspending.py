import json

import httpx

from wrike_usaspending.usaspending import USASpendingClient


def _client(handler):
    return USASpendingClient(transport=httpx.MockTransport(handler))


def test_search_awards_paginates_until_has_next_false():
    pages = {
        1: {
            "results": [{"Award ID": "A1"}, {"Award ID": "A2"}],
            "page_metadata": {"page": 1, "hasNext": True},
        },
        2: {
            "results": [{"Award ID": "A3"}],
            "page_metadata": {"page": 2, "hasNext": False},
        },
    }

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content.decode())
        assert request.url.path.endswith("/search/spending_by_award/")
        assert body["filters"]["recipient_search_text"] == ["UEI123"]
        return httpx.Response(200, json=pages[body["page"]])

    with _client(handler) as c:
        rows = list(c.search_awards_by_uei("UEI123"))
    assert [r["Award ID"] for r in rows] == ["A1", "A2", "A3"]


def test_search_awards_stops_when_results_shorter_than_page_size():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"results": [{"Award ID": "only"}], "page_metadata": {}},
        )

    with _client(handler) as c:
        rows = list(c.search_awards_by_uei("UEI", page_size=100))
    assert [r["Award ID"] for r in rows] == ["only"]


def test_search_awards_passes_award_type_codes():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content.decode())
        return httpx.Response(200, json={"results": [], "page_metadata": {"hasNext": False}})

    with _client(handler) as c:
        list(c.search_awards_by_uei("UEI"))

    codes = captured["body"]["filters"]["award_type_codes"]
    assert "A" in codes  # contracts
    assert "02" in codes  # grants
    assert "07" in codes  # loans
