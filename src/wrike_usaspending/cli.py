from __future__ import annotations

import argparse
import json
import sys

from .config import load_config
from .sync import AWARD_ID_FIELD_TITLE, sync_folder, sync_space, sync_task
from .usaspending import USASpendingClient
from .wrike import WrikeClient


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wrike-usaspending",
        description="Sync Wrike tasks with USASpending.gov awards by recipient UEI.",
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

    return 1


if __name__ == "__main__":
    sys.exit(main())
