from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from common.finding_identity import compute_finding_id_from_evidence


@dataclass
class Finding:
    employee_id: str | None
    leave_type: Optional[str]
    as_of_date: Optional[str]
    rule_code: str
    severity: str
    classification: str
    message: str
    diff_units: Optional[float] = None
    evidence: Optional[str] = None
    finding_id: Optional[str] = None
    next_action: Optional[str] = None


def compute_finding_id(rule_code: str, evidence_json: Optional[str]) -> str:
    """
    Deterministic ID based on rule_code + evidence.primary_keys.
    Stable across runs provided primary_keys remain stable.

    Raises FindingIdentityError when the evidence carries no usable primary
    keys, rather than collapsing every finding for the rule onto one ID.
    """
    return compute_finding_id_from_evidence(rule_code, evidence_json)


def _build_finding(
    rule: dict,
    employee_id: str | None,
    leave_type: str | None,
    as_of_date: str | None,
    evidence_str: str,
    diff_units: float | None = None,
) -> Finding:
    return Finding(
        employee_id=employee_id,
        leave_type=leave_type,
        as_of_date=as_of_date,
        rule_code=rule["id"],
        severity=rule["severity"],
        classification=rule.get("classification", "UNCLASSIFIED"),
        message=rule["text"]["finding"],
        diff_units=diff_units,
        evidence=evidence_str,
        finding_id=compute_finding_id(rule["id"], evidence_str),
        next_action=rule["text"]["remediation"],
    )