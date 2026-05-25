from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .sync import (
    award_to_dict,
    get_uei_from_task,
    normalize_award,
)
from .usaspending import USASpendingClient
from .wrike import WrikeClient

REPORT_SCHEMA_VERSION = 2


def _award_record(award_dict: dict[str, Any]) -> dict[str, Any]:
    return {
        "award_id": award_dict.get("award_id"),
        "recipient": award_dict.get("title"),
        "total_amount": award_dict.get("total_amount"),
        "outlay_amount": award_dict.get("outlay_amount"),
        "awarding_agency": award_dict.get("awarding_agency"),
        "award_type": award_dict.get("award_type"),
        "description": award_dict.get("description"),
        "start_date": award_dict.get("start_date"),
        "url": award_dict.get("url"),
    }


def _custom_field_value(task: dict[str, Any], field_id: str | None) -> str | None:
    if not field_id:
        return None
    for cf in task.get("customFields") or []:
        if cf.get("id") == field_id:
            value = str(cf.get("value") or "").strip()
            return value or None
    return None


def build_report(
    wrike: WrikeClient,
    usa: USASpendingClient,
    space_id: str,
    uei_field_id: str,
    *,
    program_manager_field_id: str | None = None,
    grant_number_field_id: str | None = None,
    project_title_field_id: str | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    clients: list[dict[str, Any]] = []
    for task in wrike.list_space_tasks(space_id):
        uei = get_uei_from_task(task, uei_field_id)
        if not uei:
            continue
        awards: list[dict[str, Any]] = []
        for raw in usa.search_awards_by_uei(uei):
            awards.append(_award_record(award_to_dict(normalize_award(raw))))
        awards.sort(
            key=lambda a: (a.get("total_amount") or 0.0),
            reverse=True,
        )
        clients.append(
            {
                "task_id": task["id"],
                "task_title": task.get("title"),
                "uei": uei,
                "wrike_url": f"https://www.wrike.com/open.htm?id={task['id']}",
                "program_manager": _custom_field_value(task, program_manager_field_id),
                "grant_number": _custom_field_value(task, grant_number_field_id),
                "project_title": _custom_field_value(task, project_title_field_id),
                "award_count": len(awards),
                "total_amount": sum(
                    (a.get("total_amount") or 0.0) for a in awards
                ),
                "total_outlays": sum(
                    (a.get("outlay_amount") or 0.0) for a in awards
                ),
                "awards": awards,
            }
        )

    clients.sort(key=lambda c: c["total_amount"], reverse=True)

    if now is None:
        now = datetime.now(tz=timezone.utc)

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "generated_at": now.isoformat(),
        "space_id": space_id,
        "totals": {
            "clients": len(clients),
            "awards": sum(c["award_count"] for c in clients),
            "amount": sum(c["total_amount"] for c in clients),
            "outlays": sum(c["total_outlays"] for c in clients),
        },
        "clients": clients,
    }
