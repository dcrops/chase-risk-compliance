"""Finding-producing paths for the RKEG domains that previously raised TypeError.

The EMP, LEAVE and SUP detectors omitted the required ``classification``
argument, so any rule that actually emitted a finding failed at construction
time. These tests exercise one finding-producing path per affected domain and
assert both successful construction and the classification carried from rule
configuration.
"""

from pathlib import Path

import pandas as pd
import pytest
import yaml

from rkeg.detectors import employee, leave, super_
from rkeg.models import build_finding

RULES_PATH = Path(__file__).resolve().parents[2] / "src" / "rkeg" / "config" / "rkeg_rules.yml"


def load_rule(rule_id: str) -> dict:
    rules = yaml.safe_load(RULES_PATH.read_text(encoding="utf-8"))["rules"]
    for rule in rules:
        if rule["id"] == rule_id:
            return rule
    raise AssertionError(f"{rule_id} is not defined in {RULES_PATH}")


# --------------------------------------------------------------------------
# EMP domain
# --------------------------------------------------------------------------

def test_emp_001_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-EMP-001")

    datasets = {
        "employee_master": pd.DataFrame([{"employee_id": "E001"}]),
        "pay_events": pd.DataFrame([{"employee_id": "ORPHAN1"}]),
        "leave_ledger": pd.DataFrame(),
        "leave_snapshot": pd.DataFrame(),
        "terminations": pd.DataFrame(),
    }

    findings = employee.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].employee_id == "ORPHAN1"
    assert findings[0].classification == "STRUCTURAL"
    assert findings[0].classification == rule["classification"]
    assert findings[0].finding_id


def test_emp_004_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-EMP-004")

    datasets = {
        "employee_master": pd.DataFrame(
            [{"employee_id": "E001", "employment_status": "ACTIVE"}]
        ),
        "terminations": pd.DataFrame(
            [{"employee_id": "E001", "termination_date": "2024-02-01"}]
        ),
    }

    findings = employee.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "LOGICAL"
    assert findings[0].severity == rule["severity"]


def test_emp_005_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-EMP-005")

    datasets = {
        "employee_master": pd.DataFrame([{"employee_id": "E001"}]),
        "rate_history": pd.DataFrame([{"employee_id": "E999"}]),
        "pay_events": pd.DataFrame([{"employee_id": "E001"}]),
    }

    findings = employee.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "STRUCTURAL"


# --------------------------------------------------------------------------
# LEAVE domain
# --------------------------------------------------------------------------

def test_leave_001_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-LEAVE-001")

    datasets = {
        "leave_ledger": pd.DataFrame(
            [
                {
                    "employee_id": "E001",
                    "event_date": "2024-02-05",
                    "leave_type": "ANNUAL",
                    "event_type": "TAKEN",
                    "units": -7.6,
                }
            ]
        ),
        "pay_events": pd.DataFrame(
            [{"employee_id": "E001", "pay_date": "2024-03-01"}]
        ),
    }

    findings = leave.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "LOGICAL"
    assert findings[0].leave_type == "ANNUAL"
    assert findings[0].finding_id


def test_leave_003_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-LEAVE-003")

    datasets = {
        "leave_snapshot": pd.DataFrame(
            [
                {
                    "employee_id": "E001",
                    "leave_type": "ANNUAL",
                    "as_of_date": "2024-03-31",
                    "balance_units": 120.0,
                }
            ]
        ),
        "leave_ledger": pd.DataFrame(),
    }

    findings = leave.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "STRUCTURAL"


def test_leave_004_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-LEAVE-004")

    datasets = {
        "leave_ledger": pd.DataFrame(
            [
                {
                    "employee_id": "E001",
                    "event_date": "",
                    "leave_type": "ANNUAL",
                    "event_type": "ACCRUAL",
                    "units": 7.6,
                }
            ]
        ),
    }

    findings = leave.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "STRUCTURAL"


# --------------------------------------------------------------------------
# SUP domain
# --------------------------------------------------------------------------

def test_sup_001_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-SUP-001")

    datasets = {
        "pay_events": pd.DataFrame(
            [
                {
                    "employee_id": "E001",
                    "pay_date": "2024-02-01",
                    "ote_amount": 1000.0,
                    "super_amount": 50.0,
                }
            ]
        ),
    }

    findings = super_.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "LOGICAL"
    assert findings[0].finding_id


def test_sup_004_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-SUP-004")

    datasets = {
        "employee_master": pd.DataFrame([{"employee_id": "E001"}]),
        "employee_super": pd.DataFrame(
            [{"employee_id": "E001", "default_fund_name": ""}]
        ),
    }

    findings = super_.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "STRUCTURAL"


def test_sup_006_constructs_findings_with_configured_classification():
    rule = load_rule("RKEG-SUP-006")

    datasets = {
        "employee_super": pd.DataFrame(
            [
                {"employee_id": "E001", "default_fund_name": "FUND A"},
                {"employee_id": "E001", "default_fund_name": "FUND B"},
            ]
        ),
    }

    findings = super_.run_rule(rule, datasets)

    assert len(findings) == 1
    assert findings[0].classification == "CONTEXTUAL"


# --------------------------------------------------------------------------
# Deterministic identity across reruns
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "rule_id, module, datasets_factory",
    [
        (
            "RKEG-EMP-001",
            employee,
            lambda: {
                "employee_master": pd.DataFrame([{"employee_id": "E001"}]),
                "pay_events": pd.DataFrame(
                    [{"employee_id": "ORPHAN1"}, {"employee_id": "ORPHAN2"}]
                ),
                "leave_ledger": pd.DataFrame(),
                "leave_snapshot": pd.DataFrame(),
                "terminations": pd.DataFrame(),
            },
        ),
        (
            "RKEG-LEAVE-001",
            leave,
            lambda: {
                "leave_ledger": pd.DataFrame(
                    [
                        {
                            "employee_id": "E001",
                            "event_date": "2024-02-05",
                            "leave_type": "ANNUAL",
                            "event_type": "TAKEN",
                            "units": -7.6,
                        },
                        {
                            "employee_id": "E002",
                            "event_date": "2024-02-06",
                            "leave_type": "ANNUAL",
                            "event_type": "TAKEN",
                            "units": -3.8,
                        },
                    ]
                ),
                "pay_events": pd.DataFrame(
                    [{"employee_id": "E001", "pay_date": "2024-03-01"}]
                ),
            },
        ),
        (
            "RKEG-SUP-004",
            super_,
            lambda: {
                "employee_master": pd.DataFrame(
                    [{"employee_id": "E001"}, {"employee_id": "E002"}]
                ),
                "employee_super": pd.DataFrame(
                    [
                        {"employee_id": "E001", "default_fund_name": ""},
                        {"employee_id": "E002", "default_fund_name": ""},
                    ]
                ),
            },
        ),
    ],
)
def test_rkeg_reruns_produce_stable_and_distinct_finding_ids(rule_id, module, datasets_factory):
    rule = load_rule(rule_id)

    first = module.run_rule(rule, datasets_factory())
    second = module.run_rule(rule, datasets_factory())

    first_ids = [f.finding_id for f in first]
    second_ids = [f.finding_id for f in second]

    assert first_ids == second_ids
    assert len(set(first_ids)) == len(first_ids)


def test_build_finding_rejects_findings_without_identity_evidence():
    rule = load_rule("RKEG-EMP-001")

    with pytest.raises(Exception) as excinfo:
        build_finding(
            rule,
            primary_keys={"employee_id": ""},
            employee_id=None,
            evidence="{}",
        )

    assert "RKEG-EMP-001" in str(excinfo.value)


def test_build_finding_allows_calibrated_severity_and_classification():
    rule = load_rule("RKEG-PAY-010")

    finding = build_finding(
        rule,
        primary_keys={"employee_id": "E001", "pay_date": "2024-02-01"},
        employee_id="E001",
        evidence="{}",
        severity="MEDIUM",
        classification="CONTEXTUAL",
    )

    assert finding.severity == "MEDIUM"
    assert finding.classification == "CONTEXTUAL"
    assert finding.message == rule["text"]["finding"]
    assert finding.next_action == rule["text"]["remediation"]
