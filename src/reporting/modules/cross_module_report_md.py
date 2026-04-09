from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from reporting.core.review_period import derive_review_period_from_windows
from reporting.core.structure import ReportStructure
from reporting.executive.exec_pack_md import (
    MODULE_CROSS,
    MODULE_LABELS,
    MODULE_ORDER,
    OUTPUTS_DIR,
    build_header,
    build_data_sources_section,
    load_cross_module_severity_counts,
)

from reporting.sections.exec_pack_sections import (
    build_scope_and_methodology,
    build_limitations,
    build_next_steps,
    build_appendices,
    build_cross_module_summary,
)


@dataclass
class CrossModuleFinding:
    rule_code: str
    severity: str
    employee_id: str
    leave_type: str
    as_of_date: str
    message: str
    classification: str | None = None
    evidence: str | None = None
    finding_id: str | None = None
    next_action: str | None = None

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "CrossModuleFinding":
        return cls(
            rule_code=row.get("rule_code") or row.get("rule_id") or "",
            severity=(row.get("severity") or "").upper(),
            employee_id=row.get("employee_id", "") or row.get("employee", "") or "",
            leave_type=row.get("leave_type", "") or row.get("record_type", "") or "",
            as_of_date=row.get("as_of_date", "") or row.get("snapshot_date", "") or "",
            message=row.get("message") or row.get("description") or "",
            classification=(row.get("classification") or "").upper() or None,
            evidence=row.get("evidence") or row.get("evidence_ref") or None,
            finding_id=row.get("finding_id") or None,
            next_action=row.get("next_action") or None,
        )


def _load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_cross_findings(base_output_dir: Path) -> List[CrossModuleFinding]:
    rows = _load_csv(base_output_dir / "cross_module_findings.csv")
    return [CrossModuleFinding.from_row(r) for r in rows]


def _parse_date(value: str | None) -> Optional[date]:
    if not value:
        return None

    value = value.strip()
    if not value:
        return None

    if value.lower() in {"n/a", "na", "none", "null", "unknown", "-"}:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            parsed = datetime.strptime(value, fmt).date()
            today = date.today()
            if parsed.year < 2000 or parsed.year > today.year + 1:
                return None
            return parsed
        except ValueError:
            continue

    return None


def _derive_review_period(findings: List[CrossModuleFinding], data_window_csv: Path) -> str:
    period_from_window = derive_review_period_from_windows(
        [data_window_csv],
        fallback=None,
    )
    if period_from_window:
        return period_from_window

    dates: List[date] = []
    for f in findings:
        d = _parse_date(f.as_of_date)
        if d is not None:
            dates.append(d)

    if not dates:
        return "Period not specified"

    start = min(dates)
    end = max(dates)

    if start == end:
        return start.strftime("%d %b %Y")

    return f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"


def sort_cross_findings(findings: List[CrossModuleFinding]) -> List[CrossModuleFinding]:
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(
        findings,
        key=lambda f: (
            severity_rank.get(f.severity, 99),
            f.rule_code or "",
            f.employee_id or "",
            f.as_of_date or "",
        ),
    )


def build_cross_module_summary_section(findings: List[CrossModuleFinding]) -> str:
    total_findings = len(findings)
    high = sum(1 for f in findings if f.severity == "HIGH")
    med = sum(1 for f in findings if f.severity == "MEDIUM")
    low = sum(1 for f in findings if f.severity == "LOW")

    distinct_employees = len({f.employee_id for f in findings if f.employee_id})

    lines: List[str] = []
    lines.append(
        "This Cross-Module Integrity report focuses solely on inconsistencies identified "
        "between related payroll datasets, including employee lifecycle, leave activity, "
        "payroll events, and termination-related records."
    )
    lines.append("")
    lines.append(
        f"A total of {total_findings} cross-module integrity findings were identified "
        f"across approximately {distinct_employees} employees. These findings indicate "
        "possible linkage, sequencing, lifecycle, or dataset alignment weaknesses that "
        "may reduce confidence in the broader payroll data environment."
    )
    lines.append("")
    lines.append("Across the dataset provided, the automated checks identified:")
    lines.append("")
    lines.append(f"- **High:** {high}")
    lines.append(f"- **Medium:** {med}")
    lines.append(f"- **Low:** {low}")
    lines.append("")
    lines.append(
        "A detailed breakdown by severity is provided in the **Findings Overview** section."
    )

    return "\n".join(lines).strip()


def build_cross_detailed_findings(findings: List[CrossModuleFinding]) -> str:
    if not findings:
        return """No cross-module integrity findings were identified for the supplied data.

---

"""

    lines: List[str] = []
    lines.append(
        "Each finding below follows a consistent **Finding → Evidence → Impact / Risk → Recommended Action** pattern."
    )
    lines.append("")

    for idx, f in enumerate(findings, start=1):
        lines.append(f"### Finding {idx}: {f.rule_code or 'UNSPECIFIED RULE'}")
        lines.append(f"**Severity:** {f.severity or 'UNSPECIFIED'}")
        lines.append("")

        lines.append("**Finding**")
        lines.append(f"{f.message or 'No description provided.'}")
        lines.append("")

        lines.append("**Evidence**")
        lines.append("")

        evidence_bits: List[str] = []
        if f.employee_id:
            evidence_bits.append(f"Employee ID: `{f.employee_id}`")
        if f.leave_type:
            evidence_bits.append(f"Related record / leave type: `{f.leave_type}`")
        if f.as_of_date:
            evidence_bits.append(f"As at: `{f.as_of_date}`")
        if f.classification:
            evidence_bits.append(f"Classification: `{f.classification}`")
        if f.evidence:
            evidence_bits.append(f"Evidence reference: `{f.evidence}`")
        if f.finding_id:
            evidence_bits.append(f"Finding ID: `{f.finding_id}`")
        if f.next_action:
            evidence_bits.append(f"Suggested next action (from data): `{f.next_action}`")

        if evidence_bits:
            for bit in evidence_bits:
                lines.append(f"- {bit}")
        else:
            lines.append("- Not specified in the source data.")

        lines.append("")
        lines.append("**Impact / Risk**")
        lines.append(
            "Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. "
            "These issues may reduce confidence in linked records and make payroll outcomes or employee "
            "status changes harder to explain, validate, or reconcile."
        )
        lines.append("")
        lines.append("**Recommended Action**")
        lines.append("")
        lines.append("- Validate this finding across the linked payroll, employee, leave, and termination records.")
        lines.append("- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.")
        lines.append("- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.")
        lines.append("- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_cross_appendices(base_output_dir: Path) -> str:
    return build_appendices({MODULE_CROSS}, base_output_dir)


def generate_cross_module_report(
    organisation_name: str = "Organisation not specified",
    review_period: str | None = None,
    output_dir: Path | None = None,
) -> Path:
    target_dir = output_dir or OUTPUTS_DIR
    report_path = target_dir / "cross_module_report.md"
    cross_data_window_csv = target_dir / "cross_module_data_window.csv"

    findings = load_cross_findings(target_dir)
    sorted_findings = sort_cross_findings(findings) if findings else []
    cross_counts = load_cross_module_severity_counts(target_dir)

    if review_period is None:
        review_period = (
            _derive_review_period(sorted_findings, cross_data_window_csv)
            if sorted_findings
            else "Period not specified"
        )

    parts: List[str] = []
    parts.append(
        build_header(
            "Cross-Module Integrity – Detailed Report",
            organisation_name,
            review_period,
        )
    )

    structure = ReportStructure()
    structure.add("Executive Summary", 1, build_cross_module_summary_section(sorted_findings))
    structure.add("Data Sources", 1, build_data_sources_section({MODULE_CROSS}, target_dir))
    structure.add(
        "Scope & Methodology",
        1,
        build_scope_and_methodology({MODULE_CROSS}, MODULE_LABELS, MODULE_ORDER),
    )
    structure.add("Findings Overview", 1, build_cross_module_summary(cross_counts))
    structure.add("Detailed Findings", 1, build_cross_detailed_findings(sorted_findings))
    structure.add("Limitations & Assumptions", 1, build_limitations())
    structure.add("Recommended Next Steps", 1, build_next_steps(target_dir))
    structure.add("Appendices", 1, build_cross_appendices(target_dir))

    parts.append(structure.render_markdown())
    final_md = "\n".join(parts)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(final_md, encoding="utf-8")
    return report_path