import json

import httpx
import pytest

from wrike_usaspending.wrike import WrikeClient


def _client(handler):
    return WrikeClient(token="t", transport=httpx.MockTransport(handler))


def test_find_custom_field_id_is_case_insensitive():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/customfields")
        assert request.headers["Authorization"] == "Bearer t"
        return httpx.Response(
            200,
            json={"data": [{"id": "F1", "title": "Status"}, {"id": "F2", "title": "UEI"}]},
        )

    with _client(handler) as c:
        assert c.find_custom_field_id("uei") == "F2"


def test_find_custom_field_id_raises_when_missing():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "F1", "title": "Status"}]})

    with _client(handler) as c, pytest.raises(LookupError):
        c.find_custom_field_id("uei")


def test_create_subtask_uses_parent_first_folder_when_not_provided():
    state: dict = {"posts": []}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and "/tasks/T1" in request.url.path:
            return httpx.Response(
                200,
                json={"data": [{"id": "T1", "parentIds": ["FOLDER_A", "FOLDER_B"]}]},
            )
        if request.method == "POST" and request.url.path.endswith("/folders/FOLDER_A/tasks"):
            body = json.loads(request.content.decode())
            state["posts"].append(body)
            return httpx.Response(200, json={"data": [{"id": "NEW", **body}]})
        return httpx.Response(404, json={"error": "unexpected", "path": request.url.path})

    with _client(handler) as c:
        result = c.create_subtask("T1", title="hello", description="<b>x</b>")

    assert result["id"] == "NEW"
    assert state["posts"][0]["superTasks"] == ["T1"]
    assert state["posts"][0]["title"] == "hello"


def test_create_subtask_raises_when_parent_has_no_folder():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "T1", "parentIds": []}]})

    with _client(handler) as c, pytest.raises(RuntimeError):
        c.create_subtask("T1", title="x", description="y")


def test_list_subtasks_returns_empty_when_parent_has_none():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": [{"id": "T1", "subTaskIds": []}]})

    with _client(handler) as c:
        assert c.list_subtasks("T1") == []
