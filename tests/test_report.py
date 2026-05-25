from datetime import datetime, timezone

from noa_finder.report import REPORT_SCHEMA_VERSION, build_report


class _StubWrike:
    def __init__(self, tasks):
        self._tasks = tasks
    def list_space_tasks(self, space_id):
        assert space_id == "SP1"
        return self._tasks


class _StubUSA:
    def __init__(self, by_uei):
        self._by_uei = by_uei
    def search_awards_by_uei(self, uei):
        return self._by_uei.get(uei, [])


_NOW = datetime(2026, 5, 22, 13, 0, tzinfo=timezone.utc)


def _task(task_id, title, uei=None, pm=None, grant_no=None, project=None):
    cf = []
    if uei is not None:
        cf.append({"id": "UEI", "value": uei})
    if pm is not None:
        cf.append({"id": "PM", "value": pm})
    if grant_no is not None:
        cf.append({"id": "GN", "value": grant_no})
    if project is not None:
        cf.append({"id": "PT", "value": project})
    return {"id": task_id, "title": title, "customFields": cf}


def _award(award_id, total, agency="DOD", internal_id=None,
           description=None, start_date=None):
    return {
        "Award ID": award_id,
        "Recipient Name": "Acme Inc",
        "Award Amount": total,
        "Total Outlays": total * 0.4,
        "Awarding Agency": agency,
        "Award Type": "Contract",
        "Description": description,
        "Start Date": start_date,
        "generated_internal_id": internal_id,
    }


def test_build_report_skips_tasks_without_uei():
    wrike = _StubWrike([
        _task("T1", "Acme", uei="UEI1"),
        _task("T2", "NoUei"),
    ])
    usa = _StubUSA({"UEI1": [_award("X-1", 100.0, internal_id="C1")]})
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    titles = [c["task_title"] for c in rep["clients"]]
    assert titles == ["Acme"]
    assert rep["totals"]["clients"] == 1
    assert rep["totals"]["awards"] == 1
    assert rep["totals"]["amount"] == 100.0


def test_build_report_sorts_clients_by_total_amount_desc():
    wrike = _StubWrike([
        _task("T1", "Small", uei="UEI1"),
        _task("T2", "Big", uei="UEI2"),
    ])
    usa = _StubUSA({
        "UEI1": [_award("X-1", 100.0)],
        "UEI2": [_award("X-2", 1000.0), _award("X-3", 500.0)],
    })
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    assert [c["task_title"] for c in rep["clients"]] == ["Big", "Small"]
    big = rep["clients"][0]
    assert big["award_count"] == 2
    assert big["total_amount"] == 1500.0
    assert [a["award_id"] for a in big["awards"]] == ["X-2", "X-3"]


def test_build_report_award_url_when_internal_id_present():
    wrike = _StubWrike([_task("T1", "Acme", uei="UEI1")])
    usa = _StubUSA({"UEI1": [_award("X-1", 100.0, internal_id="CAW")]})
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    award = rep["clients"][0]["awards"][0]
    assert award["url"] == "https://www.usaspending.gov/award/CAW/"


def test_build_report_award_url_none_when_internal_id_missing():
    wrike = _StubWrike([_task("T1", "Acme", uei="UEI1")])
    usa = _StubUSA({"UEI1": [_award("X-1", 100.0, internal_id=None)]})
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    assert rep["clients"][0]["awards"][0]["url"] is None


def test_build_report_metadata():
    wrike = _StubWrike([])
    usa = _StubUSA({})
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    assert rep["schema_version"] == REPORT_SCHEMA_VERSION
    assert rep["space_id"] == "SP1"
    assert rep["generated_at"] == "2026-05-22T13:00:00+00:00"
    assert rep["totals"] == {"clients": 0, "awards": 0, "amount": 0, "outlays": 0}
    assert rep["clients"] == []


def test_build_report_award_includes_start_date_and_description():
    wrike = _StubWrike([_task("T1", "Acme", uei="UEI1")])
    usa = _StubUSA({"UEI1": [_award(
        "X-1", 100.0, internal_id="CAW",
        description="Build a defense system", start_date="2024-01-15",
    )]})
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    award = rep["clients"][0]["awards"][0]
    assert award["start_date"] == "2024-01-15"
    assert award["description"] == "Build a defense system"


def test_build_report_pulls_falcon_fields_when_field_ids_provided():
    wrike = _StubWrike([
        _task("T1", "Acme", uei="UEI1",
              pm="Alice Doe", grant_no="GR-2024-001", project="Quantum sensors"),
    ])
    usa = _StubUSA({"UEI1": []})
    rep = build_report(
        wrike, usa, "SP1", "UEI", now=_NOW,
        program_manager_field_id="PM",
        grant_number_field_id="GN",
        project_title_field_id="PT",
    )
    client = rep["clients"][0]
    assert client["program_manager"] == "Alice Doe"
    assert client["grant_number"] == "GR-2024-001"
    assert client["project_title"] == "Quantum sensors"


def test_build_report_falcon_fields_null_when_field_ids_omitted():
    wrike = _StubWrike([
        _task("T1", "Acme", uei="UEI1",
              pm="Alice Doe", grant_no="GR-2024-001"),
    ])
    usa = _StubUSA({"UEI1": []})
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    client = rep["clients"][0]
    assert client["program_manager"] is None
    assert client["grant_number"] is None
    assert client["project_title"] is None


def test_build_report_wrike_url_per_client():
    wrike = _StubWrike([_task("T1", "Acme", uei="UEI1")])
    usa = _StubUSA({"UEI1": []})
    rep = build_report(wrike, usa, "SP1", "UEI", now=_NOW)
    assert rep["clients"][0]["wrike_url"] == "https://www.wrike.com/open.htm?id=T1"
