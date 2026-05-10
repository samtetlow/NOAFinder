from __future__ import annotations

import re
from typing import Any

import httpx

from ._http import default_transport

_WRIKE_ID_RE = re.compile(r"^[A-Za-z0-9]+$")
TASK_ID_BATCH = 100
DEFAULT_PAGE_SIZE = 1000


def _validate_wrike_id(value: str, field: str = "id") -> str:
    if not isinstance(value, str) or not _WRIKE_ID_RE.match(value):
        raise ValueError(
            f"Invalid Wrike {field}: must be alphanumeric, got {value!r}"
        )
    return value


class WrikeClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://www.wrike.com/api/v4",
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._http = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
            transport=transport if transport is not None else default_transport(),
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "WrikeClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def list_custom_fields(self) -> list[dict[str, Any]]:
        r = self._http.get("/customfields")
        r.raise_for_status()
        return r.json().get("data") or []

    def find_custom_field_id(self, name: str) -> str:
        target = name.strip().lower()
        for cf in self.list_custom_fields():
            if str(cf.get("title", "")).strip().lower() == target:
                return cf["id"]
        raise LookupError(
            f"Wrike custom field '{name}' not found. Run `noa-finder list-custom-fields` "
            "to see the available fields."
        )

    def ensure_custom_field(self, title: str, field_type: str = "Text") -> str:
        try:
            return self.find_custom_field_id(title)
        except LookupError:
            r = self._http.post(
                "/customfields", json={"title": title, "type": field_type}
            )
            r.raise_for_status()
            data = r.json().get("data") or []
            if not data:
                raise RuntimeError(
                    f"Wrike returned no data after creating custom field {title!r}"
                )
            return data[0]["id"]

    def list_folder_tasks(self, folder_id: str) -> list[dict[str, Any]]:
        _validate_wrike_id(folder_id, "folder_id")
        results: list[dict[str, Any]] = []
        next_token: str | None = None
        while True:
            if next_token:
                params: dict[str, Any] = {"nextPageToken": next_token}
            else:
                params = {
                    "fields": "[customFields,parentIds,subTaskIds]",
                    "pageSize": DEFAULT_PAGE_SIZE,
                }
            r = self._http.get(f"/folders/{folder_id}/tasks", params=params)
            r.raise_for_status()
            payload = r.json()
            results.extend(payload.get("data") or [])
            next_token = payload.get("nextPageToken")
            if not next_token:
                return results

    def list_spaces(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        next_token: str | None = None
        while True:
            params: dict[str, Any] = (
                {"nextPageToken": next_token} if next_token else {}
            )
            r = self._http.get("/spaces", params=params)
            r.raise_for_status()
            payload = r.json()
            results.extend(payload.get("data") or [])
            next_token = payload.get("nextPageToken")
            if not next_token:
                return results

    def list_space_folders(self, space_id: str) -> list[dict[str, Any]]:
        _validate_wrike_id(space_id, "space_id")
        r = self._http.get(
            f"/spaces/{space_id}/folders", params={"descendants": "true"}
        )
        r.raise_for_status()
        return r.json().get("data") or []

    def list_space_tasks(self, space_id: str) -> list[dict[str, Any]]:
        seen: dict[str, dict[str, Any]] = {}
        for folder in self.list_space_folders(space_id):
            for task in self.list_folder_tasks(folder["id"]):
                seen[task["id"]] = task
        return list(seen.values())

    def get_task(self, task_id: str) -> dict[str, Any]:
        _validate_wrike_id(task_id, "task_id")
        params = {"fields": "[customFields,parentIds,subTaskIds]"}
        r = self._http.get(f"/tasks/{task_id}", params=params)
        r.raise_for_status()
        items = r.json().get("data") or []
        if not items:
            raise LookupError(f"Wrike task {task_id} not found")
        return items[0]

    def get_tasks_by_ids(
        self, task_ids: list[str], fields: str = "[customFields]"
    ) -> list[dict[str, Any]]:
        if not task_ids:
            return []
        for tid in task_ids:
            _validate_wrike_id(tid, "task_id")
        results: list[dict[str, Any]] = []
        for i in range(0, len(task_ids), TASK_ID_BATCH):
            chunk = task_ids[i : i + TASK_ID_BATCH]
            r = self._http.get(
                f"/tasks/{','.join(chunk)}", params={"fields": fields}
            )
            r.raise_for_status()
            results.extend(r.json().get("data") or [])
        return results

    def list_subtasks(
        self,
        parent_task_id: str,
        parent_task: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        if parent_task is None:
            parent_task = self.get_task(parent_task_id)
        return self.get_tasks_by_ids(parent_task.get("subTaskIds") or [])

    def create_subtask(
        self,
        parent_task_id: str,
        title: str,
        description: str,
        folder_id: str | None = None,
        custom_fields: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        _validate_wrike_id(parent_task_id, "task_id")
        if folder_id is None:
            parent = self.get_task(parent_task_id)
            parent_ids = parent.get("parentIds") or []
            if not parent_ids:
                raise RuntimeError(
                    f"Parent task {parent_task_id} has no folder; cannot create "
                    "subtask. Move the task into a folder/project first."
                )
            folder_id = parent_ids[0]
        _validate_wrike_id(folder_id, "folder_id")
        body: dict[str, Any] = {
            "title": title,
            "description": description,
            "superTasks": [parent_task_id],
        }
        if custom_fields:
            body["customFields"] = custom_fields
        r = self._http.post(f"/folders/{folder_id}/tasks", json=body)
        r.raise_for_status()
        data = r.json().get("data") or []
        if not data:
            raise RuntimeError("Wrike returned no data after creating subtask")
        return data[0]
