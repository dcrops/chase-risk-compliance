"""Canonical resolution of termination evidence reference fields.

`docs/contracts/ingestion_mapping_contract.md` names ``evidence_reference`` as
the canonical termination evidence column. Extracts that have not been mapped
yet may still carry a legacy alias, so every evidence-dependent rule resolves
the value through this module rather than reading a column directly. Reading a
single alias caused TERM-005 to report missing evidence for terminations whose
canonical column was populated.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Sequence

import pandas as pd

from common.nulls import is_missing

CANONICAL_EVIDENCE_FIELD = "evidence_reference"

LEGACY_EVIDENCE_FIELDS: tuple[str, ...] = (
    "evidence_ref",
    "termination_evidence",
    "document_id",
)

EVIDENCE_FIELDS: tuple[str, ...] = (CANONICAL_EVIDENCE_FIELD,) + LEGACY_EVIDENCE_FIELDS


def resolve_evidence_reference(
    row: Mapping[str, Any] | "pd.Series",
    fields: Sequence[str] = EVIDENCE_FIELDS,
) -> Optional[str]:
    """Return the first populated evidence reference, canonical field first.

    Returns ``None`` when no candidate field carries a usable value, which is
    what the evidence-dependent rules treat as missing evidence.
    """
    for field in fields:
        try:
            value = row[field]
        except (KeyError, IndexError, TypeError):
            continue

        if is_missing(value):
            continue

        text = str(value).strip()
        if text:
            return text

    return None


def evidence_reference_series(
    df: pd.DataFrame,
    fields: Sequence[str] = EVIDENCE_FIELDS,
) -> pd.Series:
    """Return one evidence reference per row, coalescing the candidate fields.

    Rows with no usable value become an empty string so callers can test them
    with `is_missing` or a blank comparison.
    """
    resolved = pd.Series("", index=df.index, dtype="object")

    for field in fields:
        if field not in df.columns:
            continue

        candidate = df[field].map(
            lambda value: "" if is_missing(value) else str(value).strip()
        )
        resolved = resolved.where(resolved != "", candidate)

    return resolved


def has_any_evidence_field(df: pd.DataFrame, fields: Sequence[str] = EVIDENCE_FIELDS) -> bool:
    return any(field in df.columns for field in fields)
