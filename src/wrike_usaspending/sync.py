from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .usaspending import USASpendingClient
from .wrike import WrikeClient

SUBTASK_PREFIX = "[USASpending]"


@dataclass(frozen=True)
class AwardSummary:
    award_id: str
    title: str
    award_date: str | None
    total_amount: float | None
    outlayed_amount: float | None
    award_type: str | None
    awarding_agency: str | None
    description: str | None
    generated_internal_id: str | None


def _to_float(v: Any) -> float | None:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def normalize_award(raw: dict[str, Any]) -> AwardSummary:
    return AwardSummary(
        award_id=str(raw.get("Award ID") or raw.get("generated_internal_id") or "").strip(),
        title=str(raw.get("Recipient Name") or "Award").strip(),
        award_date=raw.get("Start Date"),
        total_amount=_to_float(raw.get("Award Amount")),
        outlayed_amount=_to_float(raw.get("Total Outlays")),
        award_type=raw.get("Award Type"),
        awarding_agency=raw.get("Awarding Agency"),
        description=raw.get("Description"),
        generated_internal_id=raw.get("generated_internal_id"),
    )


def _money(v: float | None) -> str:
    return f"${v:,.2f}" if v is not None else "—"


def _escape(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_subtask_title(award: AwardSummary) -> str:
    money = _money(award.total_amount) if award.total_amount is not None else "Unknown amount"
    award_id = award.award_id or "(no id)"
    return f"{SUBTASK_PREFIX} {award_id} — {money}"


def format_subtask_description(award: AwardSummary) -> str:
    rows = [
        ("Project Title", award.title),
        ("Award / Contract / Grant #", award.award_id or "—"),
        ("Award Date", award.award_date or "—"),
        ("Total Award Amount", _money(award.total_amount)),
        ("Amount Pulled Down (Outlays)", _money(award.outlayed_amount)),
        ("Award Type", award.award_type or "—"),
        ("Awarding Agency", award.awarding_agency or "—"),
    ]
    parts = ["<b>USASpending.gov Award</b>", "<table>"]
    for k, v in rows:
        parts.append(f"<tr><td><b>{k}</b></td><td>{_escape(v)}</td></tr>")
    parts.append("</table>")
    if award.description:
        parts.append(f"<br/><b>Description / Abstract</b><br/>{_escape(award.description)}")
    return "".join(parts)


def get_uei_from_task(task: dict[str, Any], uei_field_id: str) -> str | None:
    for cf in task.get("customFields") or []:
        if cf.get("id") == uei_field_id:
            value = str(cf.get("value") or "").strip()
            return value or None
    return None


def existing_award_ids(subtasks: list[dict[str, Any]]) -> set[str]:
    ids: set[str] = set()
    for t in subtasks:
        title = str(t.get("title") or "")
        if not title.startswith(SUBTASK_PREFIX):
            continue
        rest = title[len(SUBTASK_PREFIX):].strip()
        award_id = rest.split("—", 1)[0].strip()
        if award_id and award_id != "(no id)":
            ids.add(award_id)
    return ids


def sync_task(
    wrike: WrikeClient,
    usa: USASpendingClient,
    task_id: str,
    uei_field_id: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    task = wrike.get_task(task_id)
    uei = get_uei_from_task(task, uei_field_id)
    if not uei:
        return {"task_id": task_id, "skipped": True, "reason": "no UEI value"}

    folder_ids = task.get("parentIds") or []
    folder_id = folder_ids[0] if folder_ids else None

    existing_ids = existing_award_ids(wrike.list_subtasks(task_id))

    awards_found = 0
    created = 0
    skipped_existing = 0
    for raw in usa.search_awards_by_uei(uei):
        award = normalize_award(raw)
        awards_found += 1
        if award.award_id and award.award_id in existing_ids:
            skipped_existing += 1
            continue
        if dry_run:
            created += 1
            continue
        wrike.create_subtask(
            parent_task_id=task_id,
            title=format_subtask_title(award),
            description=format_subtask_description(award),
            folder_id=folder_id,
        )
        created += 1

    return {
        "task_id": task_id,
        "uei": uei,
        "awards_found": awards_found,
        "subtasks_created": created,
        "subtasks_skipped_existing": skipped_existing,
        "dry_run": dry_run,
    }


def sync_folder(
    wrike: WrikeClient,
    usa: USASpendingClient,
    folder_id: str,
    uei_field_id: str,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    return [
        sync_task(wrike, usa, t["id"], uei_field_id, dry_run=dry_run)
        for t in wrike.list_folder_tasks(folder_id)
    ]
