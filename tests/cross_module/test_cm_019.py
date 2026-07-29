"""CM-019 previously treated any recorded pay or leave activity as finalisation.

The configuration describes an absence of payroll, payout or closure activity
following termination. Pre-termination ordinary pay therefore wrongly cleared
the finding for every employee who had ever been paid.
"""

import json
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


def load_rule(rule_id: str = "CM-019") -> dict:
    rules = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))["rules"]
    for rule in rules:
        if rule["id"] == rule_id:
            return rule
    raise AssertionError(f"{rule_id} is not defined in {RULES_PATH}")


def datasets(
    *,
    pay_rows: list[dict] | None = None,
    ledger_rows: list[dict] | None = None,
) -> dict[str, pd.DataFrame]:
    return {
        "terminations": pd.DataFrame(
            [{"employee_id": "E001", "termination_date": "2024-03-01"}]
        ),
        "pay_events": pd.DataFrame(pay_rows or []),
        "leave_ledger": pd.DataFrame(ledger_rows or []),
        "leave_snapshot": pd.DataFrame(),
        "employee_master": pd.DataFrame(),
    }


def test_pre_termination_pay_alone_does_not_clear_a_silent_termination():
    findings = lifecycle_rules.detect_silent_termination(
        load_rule(),
        datasets(
            pay_rows=[{"employee_id": "E001", "pay_date": "2024-02-15"}],
            ledger_rows=[],
        ),
        {},
    )

    assert len(findings) == 1
    assert findings[0].employee_id == "E001"


def test_post_termination_pay_clears_the_finding():
    findings = lifecycle_rules.detect_silent_termination(
        load_rule(),
        datasets(
            pay_rows=[{"employee_id": "E001", "pay_date": "2024-03-10"}],
        ),
        {},
    )

    assert findings == []


def test_post_termination_closure_event_clears_the_finding():
    findings = lifecycle_rules.detect_silent_termination(
        load_rule(),
        datasets(
            ledger_rows=[
                {
                    "employee_id": "E001",
                    "leave_type": "ANNUAL",
                    "event_date": "2024-03-05",
                    "event_type": "PAYOUT",
                    "units": -20,
                }
            ],
        ),
        {},
    )

    assert findings == []


def test_pre_termination_closure_event_alone_does_not_clear_the_finding():
    findings = lifecycle_rules.detect_silent_termination(
        load_rule(),
        datasets(
            ledger_rows=[
                {
                    "employee_id": "E001",
                    "leave_type": "ANNUAL",
                    "event_date": "2024-02-01",
                    "event_type": "PAYOUT",
                    "units": -20,
                }
            ],
        ),
        {},
    )

    assert len(findings) == 1


def test_completely_silent_termination_is_still_reported():
    findings = lifecycle_rules.detect_silent_termination(
        load_rule(),
        datasets(),
        {},
    )

    assert len(findings) == 1

    payload = json.loads(findings[0].evidence)
    assert payload["values"]["assessment_basis"] == "post_termination_activity"
    assert payload["values"]["post_termination_pay_count"] == 0
    assert payload["values"]["closure_event_count"] == 0


def test_undated_extracts_degrade_to_any_recorded_activity():
    findings = lifecycle_rules.detect_silent_termination(
        load_rule(),
        {
            "terminations": pd.DataFrame(
                [{"employee_id": "E001", "termination_date": "2024-03-01"}]
            ),
            # Presence of an employee ID without a usable date is the only
            # available evidence of activity.
            "pay_events": pd.DataFrame([{"employee_id": "E001", "gross_amount": 1000}]),
            "leave_ledger": pd.DataFrame(),
            "leave_snapshot": pd.DataFrame(),
            "employee_master": pd.DataFrame(),
        },
        {},
    )

    assert findings == []


def test_empty_extracts_without_date_columns_are_treated_as_no_activity():
    findings = lifecycle_rules.detect_silent_termination(
        load_rule(),
        {
            "terminations": pd.DataFrame(
                [{"employee_id": "E001", "termination_date": "2024-03-01"}]
            ),
            "pay_events": pd.DataFrame(columns=["employee_id", "gross_amount"]),
            "leave_ledger": pd.DataFrame(columns=["employee_id", "units"]),
            "leave_snapshot": pd.DataFrame(),
            "employee_master": pd.DataFrame(),
        },
        {},
    )

    assert len(findings) == 1

    payload = json.loads(findings[0].evidence)
    assert payload["values"]["assessment_basis"] == "post_termination_activity"
    assert payload["values"]["post_termination_pay_count"] == 0
    assert payload["values"]["closure_event_count"] == 0


def test_finding_ids_remain_per_employee_and_stable():
    data = datasets()

    first = lifecycle_rules.detect_silent_termination(load_rule(), data, {})
    second = lifecycle_rules.detect_silent_termination(load_rule(), data, {})

    assert len(first) == 1
    assert [f.finding_id for f in first] == [f.finding_id for f in second]


def test_wording_describes_activity_on_or_after_termination():
    rule = load_rule()

    assert "on or after the termination date" in rule["text"]["finding"]
