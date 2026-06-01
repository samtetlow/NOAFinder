from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from .sync import (
    award_to_dict,
    get_uei_from_task,
    normalize_award,
)
from .usaspending import USASpendingClient
from .wrike import WrikeClient

REPORT_SCHEMA_VERSION = 2

logger = logging.getLogger(__name__)

# Federal UEIs are 12-character alphanumeric (sam.gov spec). Wrike UEI fields
# sometimes hold placeholders like "N/A", "TBD", or partial values that
# USASpending rejects with 422 Unprocessable Entity. Reject anything that
# doesn't look like a UEI before calling USASpending so one bad value doesn't
# tank the whole snapshot.
_UEI_RE = re.compile(r"^[A-Z0-9]{12}$")


def _looks_like_uei(value: str) -> bool:
    return bool(_UEI_RE.match(value.upper()))


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


def _fetch_awards(
    usa: USASpendingClient, uei: str, task_title: str | None,
) -> tuple[list[dict[str, Any]], str | None]:
    """Return (awards, reason_skipped). reason_skipped is None on success."""
    if not _looks_like_uei(uei):
        return [], (
            f"value '{uei}' is not a valid UEI (expected 12 alphanumeric chars)"
        )
    awards: list[dict[str, Any]] = []
    try:
        for raw in usa.search_awards_by_uei(uei):
            awards.append(_award_record(award_to_dict(normalize_award(raw))))
    except httpx.HTTPStatusError as e:
        return [], (
            f"USASpending {e.response.status_code} for {task_title!r}: "
            f"{e.response.text[:200]}"
        )
    except Exception as e:  # network errors, etc.
        return [], f"USASpending fetch failed for {task_title!r}: {e!r}"
    return awards, None


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
    skipped: list[dict[str, Any]] = []
    for task in wrike.list_space_tasks(space_id):
        uei = get_uei_from_task(task, uei_field_id)
        if not uei:
            continue
        awards, reason = _fetch_awards(usa, uei, task.get("title"))
        if reason is not None:
            logger.warning(
                "Skipping client %r (uei=%r): %s", task.get("title"), uei, reason
            )
            skipped.append(
                {
                    "task_id": task["id"],
                    "task_title": task.get("title"),
                    "uei": uei,
                    "reason": reason,
                }
            )
            # Still include the client with zero awards so the row renders
            # on the dashboard with the Falcon-side fields populated.
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
        "skipped": skipped,
        "clients": clients,
    }
