"""LSL-023 aborted the module on exactly the data it exists to report.

The rule flags LSL ledger events with a missing, invalid or future-dated event
date, but it also keyed the finding on that date. A missing date therefore
raised `FindingIdentityError` instead of producing the structural finding, and
the whole LSL module stopped.
"""

import json
from pathlib import Path

import pandas as pd
import yaml

from lsl_exposure.detectors.registry import run_rule

RULES_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "lsl_exposure"
    / "config"
    / "lsl_rules.yml"
)


def load_rule(rule_id: str = "LSL-023") -> dict:
    payload = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8")) or {}
    for rule in payload.get("rules", []):
        if rule["id"] == rule_id:
            return rule
    raise AssertionError(f"{rule_id} is not defined in {RULES_PATH}")


def datasets(ledger_rows: list[dict], snapshot_rows: list[dict] | None = None) -> dict:
    snapshot_rows = snapshot_rows if snapshot_rows is not None else [
        {
            "employee_id": "E001",
            "leave_type": "LSL",
            "as_of_date": "2024-03-31",
            "balance_units": 40,
        }
    ]

    return {
        "leave_ledger": pd.DataFrame(ledger_rows),
        "leave_snapshot": pd.DataFrame(snapshot_rows),
        "employee_master": pd.DataFrame([{"employee_id": "E001"}]),
    }


def ledger_row(**overrides) -> dict:
    row = {
        "employee_id": "E001",
        "leave_type": "LSL",
        "event_date": "2024-02-01",
        "event_type": "ACCRUAL",
        "units": 1.0,
    }
    row.update(overrides)
    return row


def test_missing_event_date_produces_a_finding_instead_of_raising():
    findings = run_rule(
        load_rule(),
        datasets([ledger_row(event_date="")]),
        context={},
    )

    assert len(findings) == 1
    assert findings[0].rule_code == "LSL-023"
    assert findings[0].finding_id


def test_unparseable_event_date_produces_a_finding():
    findings = run_rule(
        load_rule(),
        datasets([ledger_row(event_date="31/31/2024")]),
        context={},
    )

    assert len(findings) == 1


def test_identity_keys_omit_the_unusable_date_and_use_the_transaction_id():
    findings = run_rule(
        load_rule(),
        datasets([ledger_row(event_date="", transaction_id="TX-1")]),
        context={},
    )

    payload = json.loads(findings[0].evidence)

    assert "event_date" not in payload["primary_keys"]
    assert payload["primary_keys"]["transaction_id"] == "TX-1"
    assert payload["primary_keys"]["employee_id"] == "E001"


def test_identity_falls_back_to_the_source_row_without_a_transaction_id():
    findings = run_rule(
        load_rule(),
        datasets([ledger_row(event_date="")]),
        context={},
    )

    payload = json.loads(findings[0].evidence)

    assert "source_row" in payload["primary_keys"]


def test_several_invalid_rows_for_one_employee_get_distinct_identities():
    findings = run_rule(
        load_rule(),
        datasets(
            [
                ledger_row(event_date=""),
                ledger_row(event_date=""),
                ledger_row(event_date="not-a-date"),
            ]
        ),
        context={},
    )

    assert len(findings) == 3
    assert len({f.finding_id for f in findings}) == 3


def test_valid_event_dates_still_key_on_the_event_date():
    findings = run_rule(
        load_rule(),
        datasets([ledger_row(event_date="2024-12-31")]),
        context={},
    )

    payload = json.loads(findings[0].evidence)

    assert payload["primary_keys"]["event_date"] == "2024-12-31"
    assert "source_row" not in payload["primary_keys"]


def test_module_execution_continues_past_an_invalid_row():
    findings = run_rule(
        load_rule(),
        datasets(
            [
                ledger_row(event_date=""),
                ledger_row(event_date="2024-02-15"),
                ledger_row(event_date="2025-06-30"),
            ]
        ),
        context={},
    )

    # The invalid row and the future-dated row are reported; the in-window row
    # is not.
    assert len(findings) == 2


def test_identities_are_stable_across_reruns():
    ledger_rows = [ledger_row(event_date=""), ledger_row(event_date="2025-06-30")]

    first = run_rule(load_rule(), datasets(ledger_rows), context={})
    second = run_rule(load_rule(), datasets(ledger_rows), context={})

    assert [f.finding_id for f in first] == [f.finding_id for f in second]
