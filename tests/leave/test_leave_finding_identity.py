"""Identity behaviour for leave-leakage rules that fire per ledger movement.

Two rules previously emitted several findings that shared one ID:

* LEAVE-008 describes a *group* of duplicate movements but emitted one finding
  per member of the group, so every finding for the group carried the same ID.
* LEAVE-014 fires per movement, but identified movements only by employee,
  leave type and date, so two identical breaches on one date collapsed.
"""

import json

import pandas as pd
import pytest

from leave_leakage.detectors.anomaly_rules import _run_leave_008_duplicate_entries
from leave_leakage.detectors.balance_rules import _run_leave_014_taken_exceeds_balance


def _rule(rule_id: str) -> dict:
    return {
        "id": rule_id,
        "severity": "MEDIUM",
        "classification": "STRUCTURAL",
        "text": {"finding": f"{rule_id} finding text.", "remediation": "Review."},
    }


def _ledger(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["event_date"] = pd.to_datetime(df["event_date"])
    return df


def _keys(finding) -> dict:
    return json.loads(finding.evidence)["primary_keys"]


# --------------------------------------------------------------------------
# LEAVE-008: one finding per duplicate group
# --------------------------------------------------------------------------

DUPLICATE_PAIR = [
    {
        "transaction_id": "LT-0002",
        "employee_id": "E001",
        "leave_type": "ANNUAL",
        "event_date": "2024-03-11",
        "units": -7.6,
        "event_type": "TAKEN",
    },
    {
        "transaction_id": "LT-0006",
        "employee_id": "E001",
        "leave_type": "ANNUAL",
        "event_date": "2024-03-11",
        "units": -7.6,
        "event_type": "TAKEN",
    },
]


def test_leave_008_reports_a_duplicate_group_once():
    findings = _run_leave_008_duplicate_entries(_rule("LEAVE-008"), _ledger(DUPLICATE_PAIR))

    assert len(findings) == 1
    assert len({f.finding_id for f in findings}) == 1


def test_leave_008_records_the_occurrence_count_and_transactions():
    findings = _run_leave_008_duplicate_entries(_rule("LEAVE-008"), _ledger(DUPLICATE_PAIR))

    values = json.loads(findings[0].evidence)["values"]

    assert values["occurrence_count"] == 2
    assert values["transaction_ids"] == "LT-0002, LT-0006"


def test_leave_008_separates_distinct_duplicate_groups():
    rows = DUPLICATE_PAIR + [
        {
            "transaction_id": f"LT-001{i}",
            "employee_id": "E002",
            "leave_type": "ANNUAL",
            "event_date": "2024-04-02",
            "units": -3.8,
            "event_type": "TAKEN",
        }
        for i in range(2)
    ]

    findings = _run_leave_008_duplicate_entries(_rule("LEAVE-008"), _ledger(rows))

    assert len(findings) == 2
    assert len({f.finding_id for f in findings}) == 2
    assert {f.employee_id for f in findings} == {"E001", "E002"}


def test_leave_008_ignores_non_duplicated_movements():
    rows = [
        DUPLICATE_PAIR[0],
        {
            "transaction_id": "LT-0009",
            "employee_id": "E001",
            "leave_type": "ANNUAL",
            "event_date": "2024-03-12",
            "units": -7.6,
            "event_type": "TAKEN",
        },
    ]

    assert _run_leave_008_duplicate_entries(_rule("LEAVE-008"), _ledger(rows)) == []


def test_leave_008_ids_are_stable_across_reruns():
    ledger = _ledger(DUPLICATE_PAIR)
    rule = _rule("LEAVE-008")

    first = _run_leave_008_duplicate_entries(rule, ledger)
    second = _run_leave_008_duplicate_entries(rule, ledger)

    assert [f.finding_id for f in first] == [f.finding_id for f in second]


# --------------------------------------------------------------------------
# LEAVE-014: one finding per breaching movement
# --------------------------------------------------------------------------

SNAPSHOT = pd.DataFrame(
    [{"employee_id": "E001", "leave_type": "ANNUAL", "balance_units": 2.0}]
)


def test_leave_014_distinguishes_identical_breaches_on_one_date():
    findings = _run_leave_014_taken_exceeds_balance(
        _rule("LEAVE-014"), SNAPSHOT, _ledger(DUPLICATE_PAIR)
    )

    assert len(findings) == 2
    assert len({f.finding_id for f in findings}) == 2
    assert {_keys(f)["transaction_id"] for f in findings} == {"LT-0002", "LT-0006"}


def test_leave_014_distinguishes_breaches_without_transaction_ids():
    rows = [{k: v for k, v in row.items() if k != "transaction_id"} for row in DUPLICATE_PAIR]

    findings = _run_leave_014_taken_exceeds_balance(
        _rule("LEAVE-014"), SNAPSHOT, _ledger(rows)
    )

    assert len(findings) == 2
    assert len({f.finding_id for f in findings}) == 2
    assert {_keys(f)["source_row"] for f in findings} == {0, 1}


def test_leave_014_ids_are_stable_across_reruns():
    ledger = _ledger(DUPLICATE_PAIR)
    rule = _rule("LEAVE-014")

    first = _run_leave_014_taken_exceeds_balance(rule, SNAPSHOT, ledger)
    second = _run_leave_014_taken_exceeds_balance(rule, SNAPSHOT, ledger)

    assert [f.finding_id for f in first] == [f.finding_id for f in second]


def test_leave_014_does_not_flag_movements_within_balance():
    generous = pd.DataFrame(
        [{"employee_id": "E001", "leave_type": "ANNUAL", "balance_units": 100.0}]
    )

    assert (
        _run_leave_014_taken_exceeds_balance(
            _rule("LEAVE-014"), generous, _ledger(DUPLICATE_PAIR)
        )
        == []
    )


@pytest.mark.parametrize("rule_id", ["LEAVE-008", "LEAVE-014"])
def test_evidence_always_carries_primary_keys(rule_id):
    ledger = _ledger(DUPLICATE_PAIR)

    if rule_id == "LEAVE-008":
        findings = _run_leave_008_duplicate_entries(_rule(rule_id), ledger)
    else:
        findings = _run_leave_014_taken_exceeds_balance(_rule(rule_id), SNAPSHOT, ledger)

    assert findings
    for finding in findings:
        keys = _keys(finding)
        assert keys["employee_id"] == "E001"
        assert keys["event_date"] == "2024-03-11"
