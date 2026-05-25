from __future__ import annotations

import argparse
import json
import sys

from .config import load_config, load_notify_config
from .digest import build_digest
from .notify import EmailNotifier, SlackNotifier, send_digest
from .report import build_report
from .sync import AWARD_ID_FIELD_TITLE, sync_folder, sync_space, sync_task
from .usaspending import USASpendingClient
from .wrike import WrikeClient


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="noa-finder",
        description="NOA Finder: sync Wrike tasks with USASpending.gov awards by recipient UEI.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser(
        "list-custom-fields",
        help="List all Wrike custom fields (use to find your UEI field id/title)",
    )

    sub.add_parser(
        "list-spaces",
        help="List all Wrike spaces (use to find a space ID for sync-space)",
    )

    s_task = sub.add_parser("sync-task", help="Sync a single Wrike task by ID")
    s_task.add_argument("task_id")
    s_task.add_argument("--dry-run", action="store_true")

    s_folder = sub.add_parser(
        "sync-folder", help="Sync every task in a Wrike folder/project by folder ID"
    )
    s_folder.add_argument("folder_id")
    s_folder.add_argument("--dry-run", action="store_true")

    s_space = sub.add_parser(
        "sync-space", help="Sync every task across an entire Wrike space"
    )
    s_space.add_argument("space_id")
    s_space.add_argument("--dry-run", action="store_true")

    s_report = sub.add_parser(
        "build-report",
        help="Generate the JSON snapshot consumed by the NOA Finder web dashboard",
    )
    s_report.add_argument("space_id")
    s_report.add_argument(
        "--output", "-o", default="web/public/data/report.json",
        help="Path to write the report JSON (default: web/public/data/report.json)",
    )

    s_digest = sub.add_parser(
        "weekly-digest",
        help="Sync a Wrike space and send a Slack + email digest of new awards",
    )
    s_digest.add_argument("space_id")
    s_digest.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip Wrike subtask creation; still build and send the digest",
    )
    s_digest.add_argument(
        "--no-send",
        action="store_true",
        help="Build the digest and print it to stdout but do not POST/SMTP",
    )
    s_digest.add_argument(
        "--no-slack", action="store_true", help="Skip the Slack notifier"
    )
    s_digest.add_argument(
        "--no-email", action="store_true", help="Skip the email notifier"
    )

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    cfg = load_config()

    with WrikeClient(
        cfg.wrike_token, cfg.wrike_base_url, cfg.request_timeout
    ) as wrike, USASpendingClient(cfg.usaspending_base_url, cfg.request_timeout) as usa:
        if args.cmd == "list-custom-fields":
            fields = wrike.list_custom_fields()
            print(
                json.dumps(
                    [{"id": f["id"], "title": f.get("title")} for f in fields], indent=2
                )
            )
            return 0

        if args.cmd == "list-spaces":
            spaces = wrike.list_spaces()
            print(
                json.dumps(
                    [{"id": s["id"], "title": s.get("title")} for s in spaces], indent=2
                )
            )
            return 0

        uei_field_id = wrike.find_custom_field_id(cfg.wrike_uei_field_name)
        award_id_field_id = wrike.ensure_custom_field(AWARD_ID_FIELD_TITLE)

        if args.cmd == "sync-task":
            print(
                json.dumps(
                    sync_task(
                        wrike,
                        usa,
                        args.task_id,
                        uei_field_id,
                        dry_run=args.dry_run,
                        award_id_field_id=award_id_field_id,
                    ),
                    indent=2,
                )
            )
            return 0

        if args.cmd == "sync-folder":
            print(
                json.dumps(
                    sync_folder(
                        wrike,
                        usa,
                        args.folder_id,
                        uei_field_id,
                        dry_run=args.dry_run,
                        award_id_field_id=award_id_field_id,
                    ),
                    indent=2,
                )
            )
            return 0

        if args.cmd == "sync-space":
            print(
                json.dumps(
                    sync_space(
                        wrike,
                        usa,
                        args.space_id,
                        uei_field_id,
                        dry_run=args.dry_run,
                        award_id_field_id=award_id_field_id,
                    ),
                    indent=2,
                )
            )
            return 0

        if args.cmd == "weekly-digest":
            return _run_weekly_digest(
                args, wrike, usa, uei_field_id, award_id_field_id
            )

        if args.cmd == "build-report":
            return _run_build_report(args, wrike, usa, uei_field_id, cfg)

    return 1


def _maybe_find_field(wrike: WrikeClient, name: str | None) -> str | None:
    if not name:
        return None
    try:
        return wrike.find_custom_field_id(name)
    except LookupError:
        return None


def _run_build_report(
    args, wrike: WrikeClient, usa: USASpendingClient, uei_field_id: str, cfg,
) -> int:
    import os
    pm_field_id = _maybe_find_field(wrike, cfg.wrike_program_manager_field_name)
    grant_field_id = _maybe_find_field(wrike, cfg.wrike_grant_number_field_name)
    project_field_id = _maybe_find_field(wrike, cfg.wrike_project_title_field_name)
    report = build_report(
        wrike, usa, args.space_id, uei_field_id,
        program_manager_field_id=pm_field_id,
        grant_number_field_id=grant_field_id,
        project_title_field_id=project_field_id,
    )
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)
        fh.write("\n")
    print(
        json.dumps(
            {
                "output": args.output,
                "totals": report["totals"],
                "generated_at": report["generated_at"],
                "falcon_fields_resolved": {
                    "program_manager": bool(pm_field_id),
                    "grant_number": bool(grant_field_id),
                    "project_title": bool(project_field_id),
                },
            },
            indent=2,
        )
    )
    return 0


def _run_weekly_digest(
    args, wrike: WrikeClient, usa: USASpendingClient,
    uei_field_id: str, award_id_field_id: str,
) -> int:
    notify_cfg = load_notify_config()
    slack_enabled = notify_cfg.slack_enabled and not args.no_slack
    email_enabled = notify_cfg.email_enabled and not args.no_email

    if not args.no_send and not slack_enabled and not email_enabled:
        print(
            "weekly-digest: no Slack or email channel is configured. "
            "Set SLACK_WEBHOOK_URL and/or SMTP_HOST + EMAIL_FROM + EMAIL_TO, "
            "or pass --no-send to preview only.",
            file=sys.stderr,
        )
        return 2

    results = sync_space(
        wrike, usa, args.space_id, uei_field_id,
        dry_run=args.dry_run, award_id_field_id=award_id_field_id,
    )
    digest = build_digest(results, timezone_name=notify_cfg.digest_timezone)

    if args.no_send:
        print(digest.email_text)
        print(
            json.dumps(
                {
                    "summary": {
                        "total_tasks_scanned": digest.total_tasks_scanned,
                        "total_tasks_with_uei": digest.total_tasks_with_uei,
                        "total_tasks_with_new": digest.total_tasks_with_new,
                        "total_awards_found": digest.total_awards_found,
                        "total_new_subtasks": digest.total_new_subtasks,
                    },
                    "delivery": {"slack_sent": False, "email_sent": False, "skipped_send": True},
                },
                indent=2,
            )
        )
        return 0

    slack = (
        SlackNotifier(notify_cfg.slack_webhook_url)
        if slack_enabled
        else None
    )
    email = (
        EmailNotifier(
            host=notify_cfg.smtp_host or "",
            port=notify_cfg.smtp_port,
            username=notify_cfg.smtp_username,
            password=notify_cfg.smtp_password,
            from_addr=notify_cfg.email_from or "",
            to_addrs=notify_cfg.email_to,
            use_tls=notify_cfg.smtp_use_tls,
        )
        if email_enabled
        else None
    )
    try:
        report = send_digest(
            digest,
            slack=slack,
            email=email,
            notify_on_empty=notify_cfg.digest_send_when_empty,
        )
    finally:
        if slack is not None:
            slack.close()

    print(
        json.dumps(
            {
                "summary": {
                    "total_tasks_scanned": digest.total_tasks_scanned,
                    "total_tasks_with_uei": digest.total_tasks_with_uei,
                    "total_tasks_with_new": digest.total_tasks_with_new,
                    "total_awards_found": digest.total_awards_found,
                    "total_new_subtasks": digest.total_new_subtasks,
                },
                "delivery": report,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
