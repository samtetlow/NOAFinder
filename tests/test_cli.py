import json

import pytest

from noa_finder import cli


def test_parser_recognizes_sync_space():
    args = cli.build_parser().parse_args(["sync-space", "S1", "--dry-run"])
    assert args.cmd == "sync-space"
    assert args.space_id == "S1"
    assert args.dry_run is True


def test_parser_recognizes_sync_folder():
    args = cli.build_parser().parse_args(["sync-folder", "F1"])
    assert args.cmd == "sync-folder"
    assert args.folder_id == "F1"
    assert args.dry_run is False


def test_parser_recognizes_sync_task():
    args = cli.build_parser().parse_args(["sync-task", "T1"])
    assert args.cmd == "sync-task"
    assert args.task_id == "T1"


def test_parser_requires_subcommand():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args([])


def test_parser_help_exits_zero():
    with pytest.raises(SystemExit) as e:
        cli.build_parser().parse_args(["--help"])
    assert e.value.code == 0


class _FakeWrike:
    instances: list["_FakeWrike"] = []

    def __init__(self, *a, **kw):
        _FakeWrike.instances.append(self)
        self.spaces = [{"id": "SP1", "title": "Clients"}]
        self.fields = [{"id": "F1", "title": "UEI"}]

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def list_spaces(self):
        return self.spaces

    def list_custom_fields(self):
        return self.fields

    def find_custom_field_id(self, name):
        return "F1"


class _FakeUSA:
    def __init__(self, *a, **kw):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None


def _patch_clients(monkeypatch):
    monkeypatch.setenv("WRIKE_TOKEN", "test-token")
    _FakeWrike.instances.clear()
    monkeypatch.setattr(cli, "WrikeClient", _FakeWrike)
    monkeypatch.setattr(cli, "USASpendingClient", _FakeUSA)


def test_main_list_spaces(monkeypatch, capsys):
    _patch_clients(monkeypatch)
    rc = cli.main(["list-spaces"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out == [{"id": "SP1", "title": "Clients"}]


def test_main_list_custom_fields(monkeypatch, capsys):
    _patch_clients(monkeypatch)
    rc = cli.main(["list-custom-fields"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out == [{"id": "F1", "title": "UEI"}]


def test_parser_recognizes_weekly_digest():
    args = cli.build_parser().parse_args(
        ["weekly-digest", "SP1", "--dry-run", "--no-slack", "--no-email", "--no-send"]
    )
    assert args.cmd == "weekly-digest"
    assert args.space_id == "SP1"
    assert args.dry_run is True
    assert args.no_slack is True
    assert args.no_email is True
    assert args.no_send is True


def _setup_digest_env(monkeypatch):
    monkeypatch.setenv("WRIKE_TOKEN", "test-token")
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.slack.com/services/A/B")
    monkeypatch.setenv("SMTP_HOST", "mail.example.com")
    monkeypatch.setenv("EMAIL_FROM", "noa@example.com")
    monkeypatch.setenv("EMAIL_TO", "team@example.com")


class _FakeWrikeForDigest(_FakeWrike):
    def ensure_custom_field(self, title):
        return "AID"


def _stub_sync_space(monkeypatch, results):
    monkeypatch.setattr(
        cli, "sync_space", lambda *a, **kw: results
    )


def test_main_weekly_digest_no_send_prints_and_exits_zero(monkeypatch, capsys):
    _setup_digest_env(monkeypatch)
    _FakeWrike.instances.clear()
    monkeypatch.setattr(cli, "WrikeClient", _FakeWrikeForDigest)
    monkeypatch.setattr(cli, "USASpendingClient", _FakeUSA)
    _stub_sync_space(monkeypatch, [])

    rc = cli.main(["weekly-digest", "SP1", "--no-send"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "NOA Finder weekly digest" in out
    json_start = out.index("{")
    summary = json.loads(out[json_start:])
    assert summary["delivery"]["skipped_send"] is True


def test_main_weekly_digest_exits_2_when_no_channels_configured(monkeypatch, capsys):
    monkeypatch.setenv("WRIKE_TOKEN", "test-token")
    monkeypatch.delenv("SLACK_WEBHOOK_URL", raising=False)
    monkeypatch.delenv("SMTP_HOST", raising=False)
    monkeypatch.delenv("EMAIL_FROM", raising=False)
    monkeypatch.delenv("EMAIL_TO", raising=False)
    _FakeWrike.instances.clear()
    monkeypatch.setattr(cli, "WrikeClient", _FakeWrikeForDigest)
    monkeypatch.setattr(cli, "USASpendingClient", _FakeUSA)
    _stub_sync_space(monkeypatch, [])

    rc = cli.main(["weekly-digest", "SP1"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "no Slack or email channel" in err


def test_main_weekly_digest_sends_via_stub_notifiers(monkeypatch, capsys):
    _setup_digest_env(monkeypatch)
    _FakeWrike.instances.clear()
    monkeypatch.setattr(cli, "WrikeClient", _FakeWrikeForDigest)
    monkeypatch.setattr(cli, "USASpendingClient", _FakeUSA)
    _stub_sync_space(monkeypatch, [{
        "task_id": "T1", "task_title": "Acme", "uei": "U", "skipped": False,
        "reason": None, "awards_found": 1, "subtasks_created": 1,
        "subtasks_skipped_existing": 0, "subtasks_skipped_no_id": 0,
        "created_awards": [{
            "award_id": "X-1", "title": "Acme", "total_amount": 100.0,
            "outlay_amount": 50.0, "awarding_agency": "DOD",
            "award_type": "Contract", "generated_internal_id": "C",
            "url": "https://www.usaspending.gov/award/C/",
        }],
        "dry_run": False,
    }])

    sent: dict = {"slack": False, "email": False}

    class _Slack:
        def __init__(self, url): self.url = url
        def send(self, text, blocks=None): sent["slack"] = True
        def close(self): pass

    class _Email:
        def __init__(self, **kw): pass
        def send(self, **kw): sent["email"] = True

    monkeypatch.setattr(cli, "SlackNotifier", _Slack)
    monkeypatch.setattr(cli, "EmailNotifier", _Email)

    rc = cli.main(["weekly-digest", "SP1"])
    assert rc == 0
    assert sent == {"slack": True, "email": True}
