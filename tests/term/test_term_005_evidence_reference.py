"""TERM-005 read only legacy evidence aliases, never the canonical field.

Ingestion maps termination evidence to `evidence_reference`, so a correctly
mapped extract with populated evidence still raised TERM-005 for every
termination. These tests pin the canonical field and the supported aliases.
"""

import json

import pandas as pd
import pytest

from termination_exposure.detectors.registry import run_rule

RULE = {
    "id": "TERM-005",
    "severity": "MEDIUM",
    "classification": "STRUCTURAL",
    "text": {
        "finding": "Termination records do not include a supporting evidence reference.",
        "remediation": "Where available, include a reference to supporting termination documentation.",
    },
}


def datasets_with(**termination_fields) -> dict[str, pd.DataFrame]:
    row = {"employee_id": "E001", "termination_date": "2024-03-01"}
    row.update(termination_fields)

    return {
        "terminations": pd.DataFrame([row]),
        "employee_master": pd.DataFrame(),
        "pay_events": pd.DataFrame(),
        "leave_snapshot": pd.DataFrame(),
        "leave_ledger": pd.DataFrame(),
    }


def test_populated_canonical_evidence_reference_is_not_a_finding():
    findings = run_rule(RULE, datasets_with(evidence_reference="TRM-001"), context={})

    assert findings == []


def test_missing_evidence_still_raises_the_finding():
    findings = run_rule(RULE, datasets_with(evidence_reference=""), context={})

    assert len(findings) == 1
    assert findings[0].rule_code == "TERM-005"
    assert findings[0].employee_id == "E001"


def test_absent_evidence_column_still_raises_the_finding():
    findings = run_rule(RULE, datasets_with(), context={})

    assert len(findings) == 1


@pytest.mark.parametrize(
    "alias",
    ["evidence_ref", "termination_evidence", "document_id"],
)
def test_supported_legacy_aliases_clear_the_finding(alias):
    findings = run_rule(RULE, datasets_with(**{alias: "DOC-9"}), context={})

    assert findings == []


def test_canonical_field_takes_precedence_over_a_blank_legacy_alias():
    findings = run_rule(
        RULE,
        datasets_with(evidence_reference="TRM-001", evidence_ref=""),
        context={},
    )

    assert findings == []


def test_whitespace_only_evidence_counts_as_missing():
    findings = run_rule(RULE, datasets_with(evidence_reference="   "), context={})

    assert len(findings) == 1


def test_evidence_payload_names_the_canonical_field_and_fields_checked():
    findings = run_rule(RULE, datasets_with(evidence_reference=""), context={})
    payload = json.loads(findings[0].evidence)

    assert payload["values"]["evidence_reference"] is None
    assert "evidence_reference" in payload["values"]["evidence_fields_checked"]
    assert payload["primary_keys"]["employee_id"] == "E001"
    assert payload["primary_keys"]["termination_date"] == "2024-03-01"


def test_unparseable_termination_date_does_not_abort_the_rule():
    findings = run_rule(
        RULE,
        datasets_with(termination_date="not-a-date", evidence_reference=""),
        context={},
    )

    assert len(findings) == 1

    payload = json.loads(findings[0].evidence)
    assert "termination_date" not in payload["primary_keys"]
    assert findings[0].finding_id


def test_finding_ids_are_stable_across_reruns():
    first = run_rule(RULE, datasets_with(evidence_reference=""), context={})
    second = run_rule(RULE, datasets_with(evidence_reference=""), context={})

    assert [f.finding_id for f in first] == [f.finding_id for f in second]
