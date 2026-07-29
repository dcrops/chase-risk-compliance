"""CM-017 and CM-020 previously emitted evidence with no primary keys.

Every finding for those rules therefore hashed to the same ID, and duplicate
IDs are present in committed cross-module outputs. These tests pin the fix.
"""

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from cross_module_integrity.detectors import lifecycle_rules
from cross_module_integrity.models import compute_finding_id

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


def cm_017_datasets() -> dict[str, pd.DataFrame]:
    return {
        "pay_events": pd.DataFrame(
            [
                {
                    "employee_id": "E001",
                    "pay_date": "2024-01-15",
                    "run_id": "PR01",
                    "is_final_pay": "Y",
                },
                {
                    "employee_id": "E001",
                    "pay_date": "2024-02-15",
                    "run_id": "PR02",
                    "is_final_pay": "Y",
                },
                {
                    "employee_id": "E002",
                    "pay_date": "2024-01-15",
                    "run_id": "PR01",
                    "is_final_pay": "Y",
                },
            ]
        ),
        "terminations": pd.DataFrame(
            [
                {"employee_id": "E001", "termination_date": "2024-01-14", "evidence_reference": ""},
                {"employee_id": "E002", "termination_date": "2024-01-14", "evidence_reference": ""},
            ]
        ),
    }


def cm_020_datasets() -> dict[str, pd.DataFrame]:
    rows = []
    for employee_id in ("E001", "E002"):
        rows.extend(
            [
                {"employee_id": employee_id, "rule_code": "CM-001", "severity": "HIGH"},
                {"employee_id": employee_id, "rule_code": "CM-002", "severity": "HIGH"},
                {"employee_id": employee_id, "rule_code": "CM-003", "severity": "MEDIUM"},
            ]
        )
    return {"cross_module_findings": pd.DataFrame(rows)}


def test_cm_017_findings_for_different_employees_have_different_ids():
    rule = load_rule("CM-017")

    findings = lifecycle_rules.detect_final_pay_without_termination_evidence(
        rule, cm_017_datasets(), {}
    )

    assert len(findings) == 3

    by_employee = {}
    for finding in findings:
        by_employee.setdefault(finding.employee_id, []).append(finding.finding_id)

    assert set(by_employee) == {"E001", "E002"}
    assert by_employee["E001"][0] not in by_employee["E002"]


def test_cm_017_distinct_final_pays_for_one_employee_remain_distinguishable():
    rule = load_rule("CM-017")

    findings = lifecycle_rules.detect_final_pay_without_termination_evidence(
        rule, cm_017_datasets(), {}
    )

    ids = [f.finding_id for f in findings]

    assert len(set(ids)) == len(ids)


def test_cm_017_evidence_carries_primary_keys():
    rule = load_rule("CM-017")

    findings = lifecycle_rules.detect_final_pay_without_termination_evidence(
        rule, cm_017_datasets(), {}
    )

    payload = json.loads(findings[0].evidence)

    assert payload["primary_keys"]["employee_id"]
    assert payload["primary_keys"]["pay_date"]


def test_cm_017_ids_are_stable_across_reruns():
    rule = load_rule("CM-017")

    first = lifecycle_rules.detect_final_pay_without_termination_evidence(
        rule, cm_017_datasets(), {}
    )
    second = lifecycle_rules.detect_final_pay_without_termination_evidence(
        rule, cm_017_datasets(), {}
    )

    assert [f.finding_id for f in first] == [f.finding_id for f in second]


def test_cm_020_findings_for_different_employees_have_different_ids():
    rule = load_rule("CM-020")

    findings = lifecycle_rules.detect_multi_failure_cluster(rule, cm_020_datasets(), {})

    assert len(findings) == 2

    ids = [f.finding_id for f in findings]
    assert len(set(ids)) == 2


def test_cm_020_ids_are_stable_across_reruns():
    rule = load_rule("CM-020")

    first = lifecycle_rules.detect_multi_failure_cluster(rule, cm_020_datasets(), {})
    second = lifecycle_rules.detect_multi_failure_cluster(rule, cm_020_datasets(), {})

    assert [f.finding_id for f in first] == [f.finding_id for f in second]


def test_cm_020_retains_calibrated_severity_and_classification():
    rule = load_rule("CM-020")

    findings = lifecycle_rules.detect_multi_failure_cluster(rule, cm_020_datasets(), {})

    assert {f.severity for f in findings} == {"HIGH"}
    assert {f.classification for f in findings} == {"CONTEXTUAL"}


def test_cm_019_silent_termination_ids_are_per_employee():
    rule = load_rule("CM-019")

    datasets = {
        "terminations": pd.DataFrame(
            [
                {"employee_id": "E001", "termination_date": "2024-01-31"},
                {"employee_id": "E002", "termination_date": "2024-02-28"},
            ]
        ),
        "pay_events": pd.DataFrame(),
        "leave_ledger": pd.DataFrame(),
    }

    findings = lifecycle_rules.detect_silent_termination(rule, datasets, {})

    assert len(findings) == 2
    assert len({f.finding_id for f in findings}) == 2


def test_cross_module_evidence_without_primary_keys_now_fails():
    with pytest.raises(Exception) as excinfo:
        compute_finding_id("CM-017", json.dumps({"issue": "final pay without evidence"}))

    assert "primary_keys" in str(excinfo.value)
