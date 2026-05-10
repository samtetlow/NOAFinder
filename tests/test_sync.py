from wrike_usaspending.sync import (
    AwardSummary,
    existing_award_ids,
    format_subtask_description,
    format_subtask_title,
    get_uei_from_task,
    normalize_award,
)


def test_normalize_award_parses_string_money():
    raw = {
        "Award ID": "ABC-123",
        "Recipient Name": "Acme Inc",
        "Start Date": "2024-01-15",
        "Award Amount": "12345.67",
        "Total Outlays": "5000",
        "Description": "Build stuff",
        "Awarding Agency": "DOD",
        "Award Type": "Contract",
        "generated_internal_id": "CONT_AWD_X",
    }
    a = normalize_award(raw)
    assert a.award_id == "ABC-123"
    assert a.title == "Acme Inc"
    assert a.total_amount == 12345.67
    assert a.outlayed_amount == 5000.0
    assert a.award_date == "2024-01-15"
    assert a.generated_internal_id == "CONT_AWD_X"


def test_normalize_award_handles_missing_and_bad_values():
    a = normalize_award({"Award Amount": "not-a-number"})
    assert a.award_id == ""
    assert a.title == "Award"
    assert a.total_amount is None
    assert a.outlayed_amount is None


def test_normalize_award_falls_back_to_generated_internal_id():
    a = normalize_award({"generated_internal_id": "CONT_AWD_X"})
    assert a.award_id == "CONT_AWD_X"


def test_format_subtask_title_includes_id_and_money():
    a = AwardSummary("X-1", "T", "2024-01-01", 1000.0, None, None, None, None, None)
    title = format_subtask_title(a)
    assert "X-1" in title
    assert "$1,000.00" in title


def test_format_subtask_title_handles_unknown_amount():
    a = AwardSummary("X-1", "T", None, None, None, None, None, None, None)
    assert "Unknown amount" in format_subtask_title(a)


def test_format_subtask_description_includes_all_fields_and_escapes():
    a = AwardSummary(
        award_id="X-1",
        title="Recipient",
        award_date="2024-01-01",
        total_amount=1000.0,
        outlayed_amount=250.5,
        award_type="Contract",
        awarding_agency="DOD",
        description="Build a thing & <test>",
        generated_internal_id=None,
    )
    desc = format_subtask_description(a)
    assert "X-1" in desc
    assert "$1,000.00" in desc
    assert "$250.50" in desc
    assert "Contract" in desc
    assert "DOD" in desc
    assert "Build a thing &amp; &lt;test&gt;" in desc
    assert "<test>" not in desc


def test_existing_award_ids_extracts_from_titles():
    subs = [
        {"title": "[USASpending] ABC-1 — $100.00"},
        {"title": "[USASpending] DEF-2 — Unknown amount"},
        {"title": "[USASpending] (no id) — $0.00"},
        {"title": "Random other subtask"},
    ]
    assert existing_award_ids(subs) == {"ABC-1", "DEF-2"}


def test_get_uei_from_task_returns_value_when_match():
    task = {
        "customFields": [
            {"id": "F1", "value": "  ABC123  "},
            {"id": "F2", "value": "x"},
        ]
    }
    assert get_uei_from_task(task, "F1") == "ABC123"


def test_get_uei_from_task_returns_none_when_empty_or_missing():
    assert get_uei_from_task({"customFields": []}, "F1") is None
    assert get_uei_from_task({"customFields": [{"id": "F1", "value": ""}]}, "F1") is None
    assert get_uei_from_task({}, "F1") is None
