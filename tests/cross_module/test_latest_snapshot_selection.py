"""Cross-module lifecycle rules select the latest snapshot before materiality."""

from pathlib import Path

import pandas as pd
import yaml

from cross_module_integrity.detectors import lifecycle_rules

RULES_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "cross_module_integrity"
    / "config"
    / "cross_module_rules.yml"
)


def load_rule(rule_id: str) -> dict:
    rules = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))["rules"]
    for rule in rules:
        if rule["id"] == rule_id:
            return rule
    raise AssertionError(f"{rule_id} is not defined in {RULES_PATH}")


def datasets(snapshot_rows: list[dict]) -> dict[str, pd.DataFrame]:
    return {
        "terminations": pd.DataFrame(
            [{"employee_id": "E001", "termination_date": "2024-01-31"}]
        ),
        "leave_snapshot": pd.DataFrame(snapshot_rows),
        "leave_ledger": pd.DataFrame(),
        "pay_events": pd.DataFrame(),
        "employee_master": pd.DataFrame(
            [{"employee_id": "E001", "employment_status": "TERMINATED"}]
        ),
    }


CLEARED = [
    {
        "employee_id": "E001",
        "leave_type": "ANNUAL",
        "as_of_date": "2024-02-29",
        "balance_units": 40,
    },
    {
        "employee_id": "E001",
        "leave_type": "ANNUAL",
        "as_of_date": "2024-03-31",
        "balance_units": 0,
    },
]

STILL_OPEN = [
    {
        "employee_id": "E001",
        "leave_type": "ANNUAL",
        "as_of_date": "2024-02-29",
        "balance_units": 40,
    },
    {
        "employee_id": "E001",
        "leave_type": "ANNUAL",
        "as_of_date": "2024-03-31",
        "balance_units": 25,
    },
]


def test_cm_001_ignores_a_historical_balance_cleared_by_the_latest_snapshot():
    findings = lifecycle_rules.detect_terminated_employee_retains_material_leave_balance(
        load_rule("CM-001"),
        datasets(CLEARED),
        {},
    )

    assert findings == []


def test_cm_001_still_reports_a_material_latest_snapshot():
    findings = lifecycle_rules.detect_terminated_employee_retains_material_leave_balance(
        load_rule("CM-001"),
        datasets(STILL_OPEN),
        {},
    )

    assert len(findings) == 1
    assert findings[0].employee_id == "E001"
