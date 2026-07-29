import json
import math

import pytest

from common.finding_identity import (
    FindingIdentityError,
    canonical_identity,
    compute_finding_id,
    compute_finding_id_from_evidence,
)


def test_identical_rule_and_evidence_produce_the_same_id():
    first = compute_finding_id("LEAVE-005", {"employee_id": "E001", "leave_type": "ANNUAL"})
    second = compute_finding_id("LEAVE-005", {"leave_type": "ANNUAL", "employee_id": "E001"})

    assert first == second


def test_id_is_stable_across_repeated_calls():
    keys = {"employee_id": "E001", "pay_date": "2024-02-01"}
    ids = {compute_finding_id("RKEG-PAY-010", keys) for _ in range(5)}

    assert len(ids) == 1


def test_different_employees_produce_different_ids():
    first = compute_finding_id("CM-020", {"employee_id": "E001"})
    second = compute_finding_id("CM-020", {"employee_id": "E002"})

    assert first != second


def test_different_rules_produce_different_ids_for_the_same_employee():
    first = compute_finding_id("CM-017", {"employee_id": "E001"})
    second = compute_finding_id("CM-019", {"employee_id": "E001"})

    assert first != second


def test_multiple_findings_for_one_employee_and_rule_remain_distinguishable():
    january = compute_finding_id("CM-017", {"employee_id": "E001", "pay_date": "2024-01-15"})
    february = compute_finding_id("CM-017", {"employee_id": "E001", "pay_date": "2024-02-15"})

    assert january != february


def test_discriminator_distinguishes_findings_sharing_primary_keys():
    keys = {"employee_id": "E001", "previous_end": "2024-01-31", "current_start": "2024-03-01"}

    gap = compute_finding_id("RKEG-PAY-009", keys, discriminator="gap")
    overlap = compute_finding_id("RKEG-PAY-009", keys, discriminator="overlap")

    assert gap != overlap


def test_missing_primary_keys_fails_rather_than_collapsing():
    with pytest.raises(FindingIdentityError) as excinfo:
        compute_finding_id("RKEG-EMP-001", {})

    assert "RKEG-EMP-001" in str(excinfo.value)
    assert "rule code alone" in str(excinfo.value)


def test_blank_primary_key_values_fail_rather_than_collapsing():
    with pytest.raises(FindingIdentityError) as excinfo:
        compute_finding_id("RKEG-EMP-001", {"employee_id": "", "leave_type": None})

    assert "blank" in str(excinfo.value)


def test_organisation_level_findings_may_declare_empty_keys():
    finding_id = compute_finding_id("RKEG-GOV-001", {}, allow_empty_keys=True)

    assert finding_id
    assert finding_id == compute_finding_id("RKEG-GOV-001", {}, allow_empty_keys=True)


def test_non_mapping_primary_keys_fail():
    with pytest.raises(FindingIdentityError):
        compute_finding_id("RKEG-EMP-001", ["E001"])


def test_missing_rule_code_fails():
    with pytest.raises(FindingIdentityError):
        compute_finding_id("  ", {"employee_id": "E001"})


@pytest.mark.parametrize("invalid", [None, "", "   ", math.nan])
def test_invalid_primary_key_values_fail_clearly(invalid):
    with pytest.raises(FindingIdentityError) as excinfo:
        compute_finding_id("RKEG-PAY-001", {"employee_id": invalid})

    assert "employee_id" in str(excinfo.value)


def test_numeric_and_string_key_values_are_normalised_consistently():
    assert compute_finding_id("R", {"source_row": 7}) == compute_finding_id("R", {"source_row": "7"})
    assert compute_finding_id("R", {"source_row": 7.0}) == compute_finding_id("R", {"source_row": "7"})


def test_canonical_identity_is_stable_json_with_sorted_keys():
    canonical = canonical_identity(
        "CM-017", {"pay_date": "2024-01-15", "employee_id": "E001"}, discriminator="x"
    )

    assert json.loads(canonical) == {
        "discriminator": "x",
        "primary_keys": {
            "employee_id": "E001",
            "pay_date": "2024-01-15",
        },
        "rule_code": "CM-017",
    }
    assert canonical == canonical_identity(
        "CM-017", {"employee_id": "E001", "pay_date": "2024-01-15"}, discriminator="x"
    )


def test_delimiter_characters_cannot_collapse_distinct_key_sets():
    embedded_delimiters = compute_finding_id("R1", {"a": "b|c=d"})
    separate_keys = compute_finding_id("R1", {"a": "b", "c": "d"})

    assert embedded_delimiters != separate_keys


def test_evidence_based_id_reads_primary_keys():
    evidence = json.dumps({"primary_keys": {"employee_id": "E001"}})

    assert compute_finding_id_from_evidence("CM-001", evidence) == compute_finding_id(
        "CM-001", {"employee_id": "E001"}
    )


def test_malformed_evidence_fails_rather_than_collapsing():
    with pytest.raises(FindingIdentityError) as excinfo:
        compute_finding_id_from_evidence("CM-001", "{not valid json")

    assert "not valid JSON" in str(excinfo.value)


def test_evidence_without_primary_keys_entry_fails():
    evidence = json.dumps({"issue": "final pay without evidence"})

    with pytest.raises(FindingIdentityError) as excinfo:
        compute_finding_id_from_evidence("CM-017", evidence)

    assert "no primary_keys entry" in str(excinfo.value)


def test_empty_evidence_fails():
    with pytest.raises(FindingIdentityError):
        compute_finding_id_from_evidence("CM-017", "")


def test_evidence_with_non_object_primary_keys_fails():
    evidence = json.dumps({"primary_keys": ["E001"]})

    with pytest.raises(FindingIdentityError):
        compute_finding_id_from_evidence("CM-017", evidence)
