from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from zoneinfo import ZoneInfo

WRIKE_TASK_URL_TEMPLATE = "https://www.wrike.com/open.htm?id={task_id}"
SLACK_MAX_TASKS_SHOWN = 25


@dataclass(frozen=True)
class DigestPayload:
    slack_text: str
    slack_blocks: list[dict[str, Any]]
    email_subject: str
    email_text: str
    email_html: str
    total_tasks_scanned: int
    total_tasks_with_uei: int
    total_tasks_with_new: int
    total_awards_found: int
    total_new_subtasks: int


def _money(v: Any) -> str:
    if v is None:
        return "—"
    try:
        return f"${float(v):,.2f}"
    except (TypeError, ValueError):
        return "—"


def _escape(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _wrike_task_url(task_id: str) -> str:
    return WRIKE_TASK_URL_TEMPLATE.format(task_id=task_id)


def _summarize(results: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "total_tasks_scanned": len(results),
        "total_tasks_with_uei": sum(1 for r in results if not r.get("skipped")),
        "total_tasks_with_new": sum(1 for r in results if (r.get("subtasks_created") or 0) > 0),
        "total_awards_found": sum(r.get("awards_found", 0) for r in results),
        "total_new_subtasks": sum(r.get("subtasks_created", 0) for r in results),
    }


def _header_label(now: datetime, tz_name: str) -> str:
    local = now.astimezone(ZoneInfo(tz_name))
    return f"Week of {local.strftime('%a %b %-d, %Y')} ({tz_name})"


def build_digest(
    results: list[dict[str, Any]],
    *,
    timezone_name: str = "America/New_York",
    now: datetime | None = None,
) -> DigestPayload:
    counts = _summarize(results)
    if now is None:
        now = datetime.now(tz=timezone.utc)
    header = _header_label(now, timezone_name)

    tasks_with_new = [r for r in results if r.get("created_awards")]

    slack_text = _build_slack_text(header, counts, tasks_with_new)
    slack_blocks = _build_slack_blocks(header, counts, tasks_with_new)
    email_subject = (
        f"NOA Finder weekly digest — {counts['total_new_subtasks']} new awards"
    )
    email_text = _build_email_text(header, counts, tasks_with_new)
    email_html = _build_email_html(header, counts, tasks_with_new)

    return DigestPayload(
        slack_text=slack_text,
        slack_blocks=slack_blocks,
        email_subject=email_subject,
        email_text=email_text,
        email_html=email_html,
        **counts,
    )


def _build_slack_text(
    header: str, counts: dict[str, int], tasks_with_new: list[dict[str, Any]]
) -> str:
    lines = [
        f"*NOA Finder weekly digest* — {header}",
        f"{counts['total_new_subtasks']} new awards across "
        f"{counts['total_tasks_with_new']} client(s) "
        f"(scanned {counts['total_tasks_scanned']} tasks, "
        f"{counts['total_awards_found']} awards examined).",
    ]
    if not tasks_with_new:
        lines.append("_No new awards this week._")
    return "\n".join(lines)


def _build_slack_blocks(
    header: str, counts: dict[str, int], tasks_with_new: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "NOA Finder weekly digest"},
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*{header}*\n"
                    f"*{counts['total_new_subtasks']}* new awards across "
                    f"*{counts['total_tasks_with_new']}* client(s). "
                    f"Scanned {counts['total_tasks_scanned']} tasks; "
                    f"{counts['total_awards_found']} awards examined."
                ),
            },
        },
    ]
    if not tasks_with_new:
        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "_No new awards this week._"},
            }
        )
        return blocks

    shown = tasks_with_new[:SLACK_MAX_TASKS_SHOWN]
    for r in shown:
        blocks.append({"type": "divider"})
        task_url = _wrike_task_url(r["task_id"])
        title = r.get("task_title") or r["task_id"]
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{task_url}|{title}>* — {len(r['created_awards'])} new",
                },
            }
        )
        for award in r["created_awards"]:
            blocks.append(
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": _slack_award_line(award)},
                }
            )

    overflow = len(tasks_with_new) - len(shown)
    if overflow > 0:
        blocks.append(
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"_+{overflow} more client(s) not shown — see email for full list._",
                    }
                ],
            }
        )
    return blocks


def _slack_award_line(award: dict[str, Any]) -> str:
    aid = award.get("award_id") or "(no id)"
    if award.get("url"):
        head = f"<{award['url']}|{aid}>"
    else:
        head = f"`{aid}`"
    parts = [
        head,
        _money(award.get("total_amount")),
        f"outlays {_money(award.get('outlay_amount'))}",
    ]
    if award.get("awarding_agency"):
        parts.append(award["awarding_agency"])
    return " · ".join(parts)


def _build_email_text(
    header: str, counts: dict[str, int], tasks_with_new: list[dict[str, Any]]
) -> str:
    lines = [
        "NOA Finder weekly digest",
        header,
        "",
        f"{counts['total_new_subtasks']} new awards across "
        f"{counts['total_tasks_with_new']} client(s).",
        f"Scanned {counts['total_tasks_scanned']} tasks; "
        f"{counts['total_awards_found']} awards examined.",
        "",
    ]
    if not tasks_with_new:
        lines.append("No new awards this week.")
        return "\n".join(lines)
    for r in tasks_with_new:
        lines.append(
            f"- {r.get('task_title') or r['task_id']} "
            f"({_wrike_task_url(r['task_id'])})"
        )
        for award in r["created_awards"]:
            aid = award.get("award_id") or "(no id)"
            lines.append(
                f"    {aid} | "
                f"{_money(award.get('total_amount'))} | "
                f"outlays {_money(award.get('outlay_amount'))} | "
                f"{award.get('awarding_agency') or '—'}"
            )
            if award.get("url"):
                lines.append(f"      {award['url']}")
        lines.append("")
    return "\n".join(lines)


def _build_email_html(
    header: str, counts: dict[str, int], tasks_with_new: list[dict[str, Any]]
) -> str:
    parts = [
        "<html><body style=\"font-family: -apple-system, Helvetica, Arial, sans-serif;\">",
        "<h2>NOA Finder weekly digest</h2>",
        f"<p><b>{_escape(header)}</b></p>",
        "<p>",
        f"<b>{counts['total_new_subtasks']}</b> new awards across "
        f"<b>{counts['total_tasks_with_new']}</b> client(s). "
        f"Scanned {counts['total_tasks_scanned']} tasks; "
        f"{counts['total_awards_found']} awards examined.",
        "</p>",
    ]
    if not tasks_with_new:
        parts.append("<p><i>No new awards this week.</i></p></body></html>")
        return "".join(parts)
    for r in tasks_with_new:
        title = _escape(r.get("task_title") or r["task_id"])
        task_url = _wrike_task_url(r["task_id"])
        parts.append(f"<h3><a href=\"{task_url}\">{title}</a></h3>")
        parts.append(
            "<table border=\"1\" cellpadding=\"6\" cellspacing=\"0\" "
            "style=\"border-collapse: collapse; font-size: 13px;\">"
        )
        parts.append(
            "<tr style=\"background:#f0f0f0;\">"
            "<th>Award ID</th><th>Total</th><th>Outlays</th>"
            "<th>Awarding Agency</th><th>Type</th></tr>"
        )
        for award in r["created_awards"]:
            aid = _escape(award.get("award_id") or "(no id)")
            if award.get("url"):
                aid_cell = f"<a href=\"{_escape(award['url'])}\">{aid}</a>"
            else:
                aid_cell = aid
            parts.append(
                "<tr>"
                f"<td>{aid_cell}</td>"
                f"<td>{_escape(_money(award.get('total_amount')))}</td>"
                f"<td>{_escape(_money(award.get('outlay_amount')))}</td>"
                f"<td>{_escape(award.get('awarding_agency') or '—')}</td>"
                f"<td>{_escape(award.get('award_type') or '—')}</td>"
                "</tr>"
            )
        parts.append("</table>")
    parts.append("</body></html>")
    return "".join(parts)
