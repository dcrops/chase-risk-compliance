import pandas as pd

from common.evidence_fields import (
    CANONICAL_EVIDENCE_FIELD,
    EVIDENCE_FIELDS,
    evidence_reference_series,
    has_any_evidence_field,
    resolve_evidence_reference,
)


def test_canonical_field_is_first_in_precedence():
    assert EVIDENCE_FIELDS[0] == CANONICAL_EVIDENCE_FIELD == "evidence_reference"


def test_resolve_prefers_the_canonical_field():
    row = {"evidence_reference": "CANON", "evidence_ref": "LEGACY"}

    assert resolve_evidence_reference(row) == "CANON"


def test_resolve_falls_back_through_legacy_aliases():
    assert resolve_evidence_reference({"evidence_ref": "A"}) == "A"
    assert resolve_evidence_reference({"termination_evidence": "B"}) == "B"
    assert resolve_evidence_reference({"document_id": "C"}) == "C"


def test_resolve_skips_blank_and_missing_values():
    row = {"evidence_reference": "  ", "evidence_ref": None, "document_id": "D"}

    assert resolve_evidence_reference(row) == "D"


def test_resolve_returns_none_when_nothing_is_populated():
    assert resolve_evidence_reference({"evidence_reference": ""}) is None
    assert resolve_evidence_reference({}) is None


def test_series_coalesces_row_by_row():
    df = pd.DataFrame(
        [
            {"evidence_reference": "CANON", "evidence_ref": "LEGACY"},
            {"evidence_reference": "", "evidence_ref": "LEGACY"},
            {"evidence_reference": None, "evidence_ref": None},
        ]
    )

    resolved = evidence_reference_series(df)

    assert list(resolved) == ["CANON", "LEGACY", ""]


def test_series_handles_a_frame_with_no_evidence_columns():
    df = pd.DataFrame([{"employee_id": "E001"}])

    assert list(evidence_reference_series(df)) == [""]
    assert has_any_evidence_field(df) is False
