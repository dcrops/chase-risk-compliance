from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable, Mapping
import pandas as pd

from common.finding_identity import compute_finding_id


@dataclass
class Finding:
    """
    Canonical RKEG finding aligned to CRC reporting schema.
    """

    employee_id: str | None
    leave_type: str | None
    as_of_date: str | None

    rule_code: str
    severity: str
    classification: str
    message: str

    diff_units: float | None
    evidence: str
    finding_id: str
    next_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# Backwards-compatible alias for minimal detector churn
RkegFinding = Finding


def build_finding(
    rule: dict,
    *,
    primary_keys: Mapping[str, Any],
    employee_id: str | None,
    evidence: str,
    leave_type: str | None = None,
    as_of_date: str | None = None,
    message: str | None = None,
    next_action: str | None = None,
    diff_units: float | str | None = None,
    severity: str | None = None,
    classification: str | None = None,
    discriminator: str | None = None,
    allow_empty_keys: bool = False,
) -> Finding:
    """
    Construct an RKEG finding with a deterministic identity.

    Severity, classification and the finding/remediation text default to the
    rule configuration, which is the convention already used by the PAY, GOV
    and TERM detectors. ``severity`` and ``classification`` may be overridden
    where a rule calibrates them from the data (for example RKEG-PAY-010).

    ``primary_keys`` must identify the finding. Where one employee can
    legitimately raise several findings for the same rule, pass the additional
    stable keys or a ``discriminator``.
    """
    text = rule.get("text", {}) or {}

    return Finding(
        employee_id=employee_id,
        leave_type=leave_type,
        as_of_date=as_of_date,
        rule_code=rule["id"],
        severity=severity if severity is not None else rule.get("severity", "MEDIUM"),
        classification=(
            classification
            if classification is not None
            else rule.get("classification", "UNCLASSIFIED")
        ),
        message=message if message is not None else text.get("finding", ""),
        diff_units=diff_units,
        evidence=evidence,
        finding_id=compute_finding_id(
            rule["id"],
            primary_keys,
            discriminator,
            allow_empty_keys=allow_empty_keys,
        ),
        next_action=next_action if next_action is not None else text.get("remediation", ""),
    )


def findings_to_dataframe(findings: Iterable[Finding]) -> pd.DataFrame:
    rows = [f.to_dict() for f in findings]
    return pd.DataFrame(rows)


def write_findings_csv(findings: Iterable[Finding], out_path: Path) -> None:
    df = findings_to_dataframe(findings)

    if df.empty:
        df = pd.DataFrame(
            columns=[
                "employee_id",
                "leave_type",
                "as_of_date",
                "rule_code",
                "severity",
                "classification",
                "message",
                "diff_units",
                "evidence",
                "finding_id",
                "next_action",
            ]
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)