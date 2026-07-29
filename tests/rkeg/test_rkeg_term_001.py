"""RKEG-TERM-001 treated the latest post-termination pay as the final pay.

The rule reported any employee whose *last* pay on or after termination fell
outside the threshold, and its wording asserted a statutory timeframe. It now
prefers a pay event explicitly flagged as final, records which basis was used,
and describes a timing anomaly rather than a breach.
"""

import json

import pandas as pd
import pytest

from rkeg.detectors.termination import BASIS_FLAGGED, BASIS_LATEST_PAY, run_rule

from tests.rkeg.conftest import get_rule


def load_rule(rule_id: str = "RKEG-TERM-001") -> dict:
    return get_rule(rule_id)


def datasets(pay_rows: list[dict]) -> dict[str, pd.DataFrame]:
    return {
        "terminations": pd.DataFrame(
            [{"employee_id": "E001", "termination_date": "2024-03-01"}]
        ),
        "pay_events": pd.DataFrame(pay_rows),
        "employee_master": pd.DataFrame([{"employee_id": "E001"}]),
    }


def test_flagged_final_pay_within_threshold_is_not_reported():
    findings = run_rule(
        load_rule(),
        datasets(
            [
                {"employee_id": "E001", "pay_date": "2024-03-05", "is_final_pay": "Y"},
                # A later non-final adjustment must not be mistaken for final pay.
                {"employee_id": "E001", "pay_date": "2024-05-30", "is_final_pay": "N"},
            ]
        ),
    )

    assert findings == []


def test_flagged_final_pay_outside_threshold_is_reported_on_the_flagged_date():
    findings = run_rule(
        load_rule(),
        datasets(
            [
                {"employee_id": "E001", "pay_date": "2024-04-20", "is_final_pay": "Y"},
                {"employee_id": "E001", "pay_date": "2024-05-30", "is_final_pay": "N"},
            ]
        ),
    )

    assert len(findings) == 1

    payload = json.loads(findings[0].evidence)
    assert payload["values"]["final_pay_basis"] == BASIS_FLAGGED
    assert payload["values"]["derived_final_pay_date"] == "2024-04-20"
    assert payload["values"]["days_after_termination"] == 50


def test_earliest_flagged_final_pay_is_used_when_several_are_flagged():
    findings = run_rule(
        load_rule(),
        datasets(
            [
                {"employee_id": "E001", "pay_date": "2024-04-20", "is_final_pay": "Y"},
                {"employee_id": "E001", "pay_date": "2024-06-20", "is_final_pay": "Y"},
            ]
        ),
    )

    payload = json.loads(findings[0].evidence)
    assert payload["values"]["derived_final_pay_date"] == "2024-04-20"


def test_unflagged_pay_falls_back_to_latest_pay_and_records_the_lower_certainty_basis():
    findings = run_rule(
        load_rule(),
        datasets(
            [
                {"employee_id": "E001", "pay_date": "2024-03-05", "is_final_pay": "N"},
                {"employee_id": "E001", "pay_date": "2024-04-20", "is_final_pay": "N"},
            ]
        ),
    )

    assert len(findings) == 1

    payload = json.loads(findings[0].evidence)
    assert payload["values"]["final_pay_basis"] == BASIS_LATEST_PAY
    assert payload["values"]["derived_final_pay_date"] == "2024-04-20"
    assert "proxy" in payload["explanation"]
    assert "confirm the actual final pay date" in payload["explanation"].lower()


def test_missing_final_pay_flag_column_still_produces_a_proxy_finding():
    findings = run_rule(
        load_rule(),
        datasets([{"employee_id": "E001", "pay_date": "2024-04-20"}]),
    )

    payload = json.loads(findings[0].evidence)
    assert payload["values"]["final_pay_basis"] == BASIS_LATEST_PAY
    assert payload["values"]["final_pay_flag_available"] is False


def test_one_finding_per_employee_termination_with_a_stable_identity():
    pay_rows = [
        {"employee_id": "E001", "pay_date": "2024-04-20", "is_final_pay": "Y"},
        {"employee_id": "E001", "pay_date": "2024-05-20", "is_final_pay": "N"},
    ]

    first = run_rule(load_rule(), datasets(pay_rows))
    second = run_rule(load_rule(), datasets(pay_rows))

    assert len(first) == 1
    assert len({f.finding_id for f in first}) == 1
    assert [f.finding_id for f in first] == [f.finding_id for f in second]


def test_wording_does_not_assert_a_legal_breach():
    rule = load_rule()
    text = " ".join(rule["text"].values()).lower()

    for phrase in ("statutory timeframe", "breach fair work", "non-compliant"):
        assert phrase not in text

    findings = run_rule(
        load_rule(),
        datasets([{"employee_id": "E001", "pay_date": "2024-04-20", "is_final_pay": "Y"}]),
    )

    payload = json.loads(findings[0].evidence)
    assert "not a determination" in payload["explanation"]


@pytest.mark.parametrize("flag", ["Y", "yes", "TRUE", "1", "t"])
def test_common_truthy_final_pay_flags_are_recognised(flag):
    findings = run_rule(
        load_rule(),
        datasets(
            [
                {"employee_id": "E001", "pay_date": "2024-03-05", "is_final_pay": flag},
                {"employee_id": "E001", "pay_date": "2024-04-20", "is_final_pay": "N"},
            ]
        ),
    )

    assert findings == []
