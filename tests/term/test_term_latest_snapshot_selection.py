"""TERM-007 and TERM-009 tested materiality before selecting the latest snapshot.

Where an extract carried several snapshots per employee, a historical material
balance raised a current finding even though the latest snapshot showed the
balance had been cleared.
"""

import json

import pandas as pd

from termination_exposure.detectors.registry import run_rule

TERM_007 = {
    "id": "TERM-007",
    "severity": "HIGH",
    "classification": "CONTEXTUAL",
    "config": {"material_balance_units": 10, "snapshot_grace_days": 14},
    "text": {
        "finding": "A terminated employee retains a material LSL balance in the snapshot extract.",
        "remediation": "Confirm whether the LSL was paid or intentionally remains open.",
    },
}

TERM_009 = {
    "id": "TERM-009",
    "severity": "MEDIUM",
    "classification": "CONTEXTUAL",
    "config": {
        "material_balance_units": 10,
        "snapshot_grace_days": 14,
        "closure_event_types": ["TAKEN", "ADJUSTMENT", "PAYOUT"],
    },
    "text": {
        "finding": "A terminated employee retains a material LSL balance with no closure trail.",
        "remediation": "Confirm whether the balance was closed outside the ledger extract.",
    },
}


def datasets(snapshot_rows: list[dict], ledger_rows: list[dict] | None = None) -> dict:
    return {
        "terminations": pd.DataFrame(
            [{"employee_id": "T1", "termination_date": "2024-01-31"}]
        ),
        "leave_snapshot": pd.DataFrame(snapshot_rows),
        "leave_ledger": pd.DataFrame(ledger_rows or []),
        "pay_events": pd.DataFrame(),
        "employee_master": pd.DataFrame(),
    }


def snapshot_row(as_of_date: str, balance_units) -> dict:
    return {
        "employee_id": "T1",
        "leave_type": "LSL",
        "as_of_date": as_of_date,
        "balance_units": balance_units,
    }


CLEARED_AFTER_MATERIAL = [
    snapshot_row("2024-02-29", 40),
    snapshot_row("2024-03-31", 0),
]

STILL_MATERIAL = [
    snapshot_row("2024-02-29", 40),
    snapshot_row("2024-03-31", 25),
]


def test_term_007_ignores_a_historical_balance_cleared_by_the_latest_snapshot():
    findings = run_rule(TERM_007, datasets(CLEARED_AFTER_MATERIAL), context={})

    assert findings == []


def test_term_007_still_reports_a_material_latest_snapshot():
    findings = run_rule(TERM_007, datasets(STILL_MATERIAL), context={})

    assert len(findings) == 1

    payload = json.loads(findings[0].evidence)
    assert payload["primary_keys"]["snapshot_date"] == "2024-03-31"
    assert payload["values"]["lsl_balance_units"] == 25.0


def test_term_009_ignores_a_historical_balance_cleared_by_the_latest_snapshot():
    findings = run_rule(TERM_009, datasets(CLEARED_AFTER_MATERIAL), context={})

    assert findings == []


def test_term_009_still_reports_a_material_latest_snapshot_without_a_closure_trail():
    findings = run_rule(TERM_009, datasets(STILL_MATERIAL), context={})

    assert len(findings) == 1
    assert findings[0].rule_code == "TERM-009"


def test_term_009_closure_activity_still_suppresses_the_finding():
    findings = run_rule(
        TERM_009,
        datasets(
            STILL_MATERIAL,
            ledger_rows=[
                {
                    "employee_id": "T1",
                    "leave_type": "LSL",
                    "event_date": "2024-02-15",
                    "event_type": "PAYOUT",
                    "units": -25,
                }
            ],
        ),
        context={},
    )

    assert findings == []


def test_single_material_snapshot_behaviour_is_unchanged():
    findings = run_rule(TERM_007, datasets([snapshot_row("2024-03-31", 25)]), context={})

    assert len(findings) == 1


def test_latest_snapshot_below_the_threshold_is_not_reported():
    findings = run_rule(
        TERM_007,
        datasets([snapshot_row("2024-02-29", 40), snapshot_row("2024-03-31", 5)]),
        context={},
    )

    assert findings == []
