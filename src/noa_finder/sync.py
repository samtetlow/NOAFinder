from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .usaspending import USASpendingClient
from .wrike import WrikeClient

SUBTASK_PREFIX = "[USASpending]"
AWARD_ID_FIELD_TITLE = "USASpending Award ID"
DESCRIPTION_MAX_CHARS = 30000


@dataclass(frozen=True)
class AwardSummary:
    award_id: str
    title: str
    award_date: str | None
    total_amount: float | None
    outlay_amount: float | None
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
        outlay_amount=_to_float(raw.get("Total Outlays")),
        award_type=raw.get("Award Type"),
        awarding_agency=raw.get("Awarding Agency"),
        description=raw.get("Description"),
        generated_internal_id=raw.get("generated_internal_id"),
    )


def usaspending_award_url(generated_internal_id: str | None) -> str | None:
    if not generated_internal_id:
        return None
    return f"https://www.usaspending.gov/award/{generated_internal_id}/"


def award_to_dict(award: AwardSummary) -> dict[str, Any]:
    return {
        "award_id": award.award_id,
        "title": award.title,
        "total_amount": award.total_amount,
        "outlay_amount": award.outlay_amount,
        "awarding_agency": award.awarding_agency,
        "award_type": award.award_type,
        "generated_internal_id": award.generated_internal_id,
        "url": usaspending_award_url(award.generated_internal_id),
    }


def _money(v: float | None) -> str:
    return f"${v:,.2f}" if v is not None else "—"


def _escape(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _truncate(s: str, limit: int = DESCRIPTION_MAX_CHARS) -> str:
    if len(s) <= limit:
        return s
    suffix = "…[truncated]"
    return s[: limit - len(suffix)] + suffix


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
        ("Amount Pulled Down (Outlays)", _money(award.outlay_amount)),
        ("Award Type", award.award_type or "—"),
        ("Awarding Agency", award.awarding_agency or "—"),
    ]
    parts = ["<b>USASpending.gov Award</b>", "<table>"]
    for k, v in rows:
        parts.append(f"<tr><td><b>{k}</b></td><td>{_escape(v)}</td></tr>")
    parts.append("</table>")
    if award.description:
        parts.append(
            f"<br/><b>Description / Abstract</b><br/>{_escape(award.description)}"
        )
    return _truncate("".join(parts))


def get_uei_from_task(task: dict[str, Any], uei_field_id: str) -> str | None:
    for cf in task.get("customFields") or []:
        if cf.get("id") == uei_field_id:
            value = str(cf.get("value") or "").strip()
            return value or None
    return None


def _award_id_from_title(title: str) -> str | None:
    if not title.startswith(SUBTASK_PREFIX):
        return None
    rest = title[len(SUBTASK_PREFIX):].strip()
    aid = rest.split("—", 1)[0].strip()
    return aid if aid and aid != "(no id)" else None


def _award_id_from_custom_field(
    task: dict[str, Any], field_id: str
) -> str | None:
    for cf in task.get("customFields") or []:
        if cf.get("id") == field_id:
            value = str(cf.get("value") or "").strip()
            return value or None
    return None


def existing_award_ids(
    subtasks: list[dict[str, Any]],
    award_id_field_id: str | None = None,
) -> set[str]:
    ids: set[str] = set()
    for t in subtasks:
        aid: str | None = None
        if award_id_field_id:
            aid = _award_id_from_custom_field(t, award_id_field_id)
        if not aid:
            aid = _award_id_from_title(str(t.get("title") or ""))
        if aid:
            ids.add(aid)
    return ids


def _empty_result(task_id: str, dry_run: bool) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "task_title": None,
        "uei": None,
        "skipped": False,
        "reason": None,
        "awards_found": 0,
        "subtasks_created": 0,
        "subtasks_skipped_existing": 0,
        "subtasks_skipped_no_id": 0,
        "created_awards": [],
        "dry_run": dry_run,
    }


def sync_task(
    wrike: WrikeClient,
    usa: USASpendingClient,
    task_id: str,
    uei_field_id: str,
    dry_run: bool = False,
    *,
    task: dict[str, Any] | None = None,
    award_id_field_id: str | None = None,
) -> dict[str, Any]:
    result = _empty_result(task_id, dry_run)

    if task is None:
        task = wrike.get_task(task_id)
    result["task_title"] = task.get("title")

    uei = get_uei_from_task(task, uei_field_id)
    if not uei:
        result["skipped"] = True
        result["reason"] = "no UEI value"
        return result
    result["uei"] = uei

    folder_ids = task.get("parentIds") or []
    folder_id = folder_ids[0] if folder_ids else None

    existing_ids = existing_award_ids(
        wrike.list_subtasks(task_id, parent_task=task),
        award_id_field_id=award_id_field_id,
    )

    for raw in usa.search_awards_by_uei(uei):
        award = normalize_award(raw)
        result["awards_found"] += 1
        if not award.award_id:
            result["subtasks_skipped_no_id"] += 1
            continue
        if award.award_id in existing_ids:
            result["subtasks_skipped_existing"] += 1
            continue
        if dry_run:
            result["subtasks_created"] += 1
            result["created_awards"].append(award_to_dict(award))
            existing_ids.add(award.award_id)
            continue
        custom_fields = (
            [{"id": award_id_field_id, "value": award.award_id}]
            if award_id_field_id
            else None
        )
        wrike.create_subtask(
            parent_task_id=task_id,
            title=format_subtask_title(award),
            description=format_subtask_description(award),
            folder_id=folder_id,
            custom_fields=custom_fields,
        )
        existing_ids.add(award.award_id)
        result["subtasks_created"] += 1
        result["created_awards"].append(award_to_dict(award))

    return result


def sync_folder(
    wrike: WrikeClient,
    usa: USASpendingClient,
    folder_id: str,
    uei_field_id: str,
    dry_run: bool = False,
    *,
    award_id_field_id: str | None = None,
) -> list[dict[str, Any]]:
    return [
        sync_task(
            wrike,
            usa,
            t["id"],
            uei_field_id,
            dry_run=dry_run,
            task=t,
            award_id_field_id=award_id_field_id,
        )
        for t in wrike.list_folder_tasks(folder_id)
    ]


def sync_space(
    wrike: WrikeClient,
    usa: USASpendingClient,
    space_id: str,
    uei_field_id: str,
    dry_run: bool = False,
    *,
    award_id_field_id: str | None = None,
) -> list[dict[str, Any]]:
    return [
        sync_task(
            wrike,
            usa,
            t["id"],
            uei_field_id,
            dry_run=dry_run,
            task=t,
            award_id_field_id=award_id_field_id,
        )
        for t in wrike.list_space_tasks(space_id)
    ]
