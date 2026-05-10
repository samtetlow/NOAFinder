from __future__ import annotations

from typing import Any

import httpx


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
            transport=transport,
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
            f"Wrike custom field '{name}' not found. Run `wrike-usaspending list-custom-fields` "
            "to see the available fields."
        )

    def list_folder_tasks(self, folder_id: str) -> list[dict[str, Any]]:
        params = {"fields": "[customFields,parentIds,subTaskIds]"}
        r = self._http.get(f"/folders/{folder_id}/tasks", params=params)
        r.raise_for_status()
        return r.json().get("data") or []

    def get_task(self, task_id: str) -> dict[str, Any]:
        params = {"fields": "[customFields,parentIds,subTaskIds]"}
        r = self._http.get(f"/tasks/{task_id}", params=params)
        r.raise_for_status()
        items = r.json().get("data") or []
        if not items:
            raise LookupError(f"Wrike task {task_id} not found")
        return items[0]

    def list_subtasks(self, parent_task_id: str) -> list[dict[str, Any]]:
        parent = self.get_task(parent_task_id)
        sub_ids = parent.get("subTaskIds") or []
        if not sub_ids:
            return []
        params = {"fields": "[customFields]"}
        r = self._http.get(f"/tasks/{','.join(sub_ids)}", params=params)
        r.raise_for_status()
        return r.json().get("data") or []

    def create_subtask(
        self,
        parent_task_id: str,
        title: str,
        description: str,
        folder_id: str | None = None,
    ) -> dict[str, Any]:
        if folder_id is None:
            parent = self.get_task(parent_task_id)
            parent_ids = parent.get("parentIds") or []
            if not parent_ids:
                raise RuntimeError(
                    f"Parent task {parent_task_id} has no folder; cannot create subtask. "
                    "Move the task into a folder/project first."
                )
            folder_id = parent_ids[0]
        body = {
            "title": title,
            "description": description,
            "superTasks": [parent_task_id],
        }
        r = self._http.post(f"/folders/{folder_id}/tasks", json=body)
        r.raise_for_status()
        return r.json()["data"][0]
