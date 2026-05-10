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


def test_list_folder_tasks_follows_next_page_token():
    pages = [
        {"data": [{"id": "T1"}, {"id": "T2"}], "nextPageToken": "tok1"},
        {"data": [{"id": "T3"}]},
    ]
    calls: list[dict] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(dict(request.url.params))
        return httpx.Response(200, json=pages[len(calls) - 1])

    with _client(handler) as c:
        ids = [t["id"] for t in c.list_folder_tasks("F1")]

    assert ids == ["T1", "T2", "T3"]
    assert "fields" in calls[0]
    assert calls[1] == {"nextPageToken": "tok1"}


def test_list_spaces_returns_data():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/spaces")
        return httpx.Response(
            200,
            json={"data": [{"id": "S1", "title": "Clients"}, {"id": "S2", "title": "Internal"}]},
        )

    with _client(handler) as c:
        spaces = c.list_spaces()
    assert [s["id"] for s in spaces] == ["S1", "S2"]


def test_list_space_tasks_walks_folders_and_dedupes():
    folders = {"data": [{"id": "F1"}, {"id": "F2"}]}
    folder_tasks = {
        "F1": {"data": [{"id": "T1"}, {"id": "T2"}]},
        "F2": {"data": [{"id": "T2"}, {"id": "T3"}]},
    }

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/spaces/S1/folders"):
            return httpx.Response(200, json=folders)
        for fid, payload in folder_tasks.items():
            if path.endswith(f"/folders/{fid}/tasks"):
                return httpx.Response(200, json=payload)
        return httpx.Response(404, json={"path": path})

    with _client(handler) as c:
        ids = sorted(t["id"] for t in c.list_space_tasks("S1"))
    assert ids == ["T1", "T2", "T3"]
