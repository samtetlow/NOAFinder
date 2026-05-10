from datetime import datetime, timezone

from noa_finder.digest import SLACK_MAX_TASKS_SHOWN, build_digest


def _result(
    task_id="T1",
    task_title="Acme Inc",
    skipped=False,
    awards_found=0,
    subtasks_created=0,
    created_awards=None,
):
    return {
        "task_id": task_id,
        "task_title": task_title,
        "uei": "UEI123" if not skipped else None,
        "skipped": skipped,
        "reason": "no UEI value" if skipped else None,
        "awards_found": awards_found,
        "subtasks_created": subtasks_created,
        "subtasks_skipped_existing": 0,
        "subtasks_skipped_no_id": 0,
        "created_awards": created_awards or [],
        "dry_run": False,
    }


def _award(award_id="X-1", url="https://www.usaspending.gov/award/CONT_AWD_X/"):
    return {
        "award_id": award_id,
        "title": "Acme",
        "total_amount": 1000.0,
        "outlay_amount": 250.0,
        "awarding_agency": "DOD",
        "award_type": "Contract",
        "generated_internal_id": "CONT_AWD_X" if url else None,
        "url": url,
    }


_NOW = datetime(2026, 5, 4, 13, 0, tzinfo=timezone.utc)


def test_build_digest_empty_results():
    d = build_digest([], now=_NOW)
    assert d.total_tasks_scanned == 0
    assert d.total_new_subtasks == 0
    assert "No new awards" in d.email_text
    assert "No new awards" in d.slack_text


def test_build_digest_no_new_subtasks():
    d = build_digest(
        [_result(awards_found=2, subtasks_created=0)], now=_NOW
    )
    assert d.total_tasks_scanned == 1
    assert d.total_tasks_with_uei == 1
    assert d.total_new_subtasks == 0
    assert d.total_tasks_with_new == 0
    assert "No new awards" in d.email_text


def test_build_digest_groups_by_task_only_with_new():
    awards = [_award("X-1"), _award("X-2", url=None)]
    results = [
        _result("T1", task_title="Acme", awards_found=2, subtasks_created=2,
                created_awards=awards),
        _result("T2", task_title="NoNew", awards_found=3, subtasks_created=0),
        _result("T3", task_title="SkippedNoUei", skipped=True),
    ]
    d = build_digest(results, now=_NOW)
    assert d.total_tasks_scanned == 3
    assert d.total_tasks_with_uei == 2
    assert d.total_tasks_with_new == 1
    assert d.total_new_subtasks == 2
    assert d.total_awards_found == 5
    assert "Acme" in d.email_text
    assert "NoNew" not in d.email_text
    assert "SkippedNoUei" not in d.email_text


def test_build_digest_uses_internal_id_for_url():
    results = [
        _result("T1", "Acme", awards_found=1, subtasks_created=1,
                created_awards=[_award("X-1")])
    ]
    d = build_digest(results, now=_NOW)
    assert "https://www.usaspending.gov/award/CONT_AWD_X/" in d.email_html
    assert "CONT_AWD_X" in d.slack_text or "CONT_AWD_X" in str(d.slack_blocks)


def test_build_digest_omits_url_when_internal_id_missing():
    results = [
        _result("T1", "Acme", awards_found=1, subtasks_created=1,
                created_awards=[_award("X-1", url=None)])
    ]
    d = build_digest(results, now=_NOW)
    assert "usaspending.gov/award/" not in d.email_html
    assert "X-1" in d.email_html


def test_build_digest_caps_slack_tasks_with_overflow_note():
    n = SLACK_MAX_TASKS_SHOWN + 5
    results = [
        _result(f"T{i}", f"Client{i}", awards_found=1, subtasks_created=1,
                created_awards=[_award(f"X-{i}")])
        for i in range(n)
    ]
    d = build_digest(results, now=_NOW)
    overflow_block = d.slack_blocks[-1]
    assert overflow_block["type"] == "context"
    assert "5 more" in overflow_block["elements"][0]["text"]
    assert d.total_tasks_with_new == n


def test_build_digest_includes_timezone_in_header():
    d = build_digest([], now=_NOW, timezone_name="America/New_York")
    assert "America/New_York" in d.slack_text
    assert "2026" in d.slack_text


def test_build_digest_subject_includes_count():
    results = [
        _result("T1", "Acme", awards_found=1, subtasks_created=1,
                created_awards=[_award("X-1")])
    ]
    d = build_digest(results, now=_NOW)
    assert "1 new awards" in d.email_subject
