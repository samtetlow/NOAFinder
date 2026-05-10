import json

import pytest

from wrike_usaspending import cli


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
