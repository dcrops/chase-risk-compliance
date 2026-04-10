from __future__ import annotations

import csv
from datetime import date, datetime
from html import escape
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
    build_finding_meta,
)

from reporting.core.cover_page import build_cover_page


@dataclass
class CrossModuleFinding:
    rule_code: str
    severity: str
    employee_id: str
    leave_type: str
    as_of_date: str
    message: str
    classification: str | None = None
    termination_date: str | None = None
    event_date: str | None = None
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
            termination_date=row.get("termination_date") or None,
            event_date=row.get("event_date") or None,
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


def _severity_class(severity: str) -> str:
    s = (severity or "").upper()
    if s == "HIGH":
        return "high"
    if s == "MEDIUM":
        return "medium"
    if s == "LOW":
        return "low"
    return "info"


def _render_labeled_section(label: str, body: str, extra_class: str = "") -> str:
    class_attr = f"finding-text {extra_class}".strip()
    return f"""
<div class="finding-section">
  <div class="finding-label">{escape(label)}</div>
  <div class="{class_attr}">{body}</div>
</div>
""".strip()


def render_cross_finding_card(f: CrossModuleFinding) -> str:
    severity = (f.severity or "").upper() or "INFO"
    severity_class = _severity_class(severity)

    rule_code = escape(f.rule_code or "UNSPECIFIED RULE")
    message = escape(f.message or "No description provided.")
    recommendation_text = f.next_action or (
        "Validate the finding across linked payroll, employee, leave, and termination records, "
        "confirm whether the inconsistency reflects a true process issue, timing difference, or "
        "source-system mismatch, and correct any confirmed alignment or lifecycle sequencing issues."
    )

    date_part = None

    if f.termination_date and f.event_date:
        date_part = f"Dates: {f.termination_date} → {f.event_date}"
    elif f.termination_date:
        date_part = f"Termination: {f.termination_date}"
    elif f.event_date:
        date_part = f"Event: {f.event_date}"
    elif f.as_of_date:
        date_part = f"As at: {f.as_of_date}"

    extra_parts = [date_part] if date_part else None

    meta_text = build_finding_meta(
        employee_id=f.employee_id or None,
        context_label="Related record / leave type",
        context_value=f.leave_type or None,
        date_label=None,
        date_value=None,
        classification=f.classification or None,
        extra_parts=extra_parts,
    )

    impact = (
        "This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll "
        "datasets. These issues can reduce confidence in linked records and make payroll outcomes or "
        "employee status changes harder to explain, validate, or reconcile."
    )

    sections: list[str] = [
        _render_labeled_section("Finding", message, "finding-main"),
        _render_labeled_section("Impact", escape(impact), "finding-impact"),
        _render_labeled_section("Recommendation", escape(recommendation_text), "finding-action"),
    ]

    if f.finding_id:
        sections.append(
            _render_labeled_section("Finding ID", escape(f.finding_id))
        )

    if f.evidence:
        sections.append(
            """
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">"""
            + escape(f.evidence)
            + """</pre>
</div>
""".strip()
        )

    section_html = "\n  ".join(sections)

    return f"""
<div class="finding {severity_class}">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">{rule_code}</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-{severity_class}">{escape(severity)}</span>
    </div>
  </div>

  <div class="finding-meta">{meta_text}</div>

  {section_html}
</div>
""".strip()


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
        return """
<div class="no-findings">
No cross-module integrity findings were identified for the supplied data.
</div>
""".strip()

    intro = """
This section sets out detailed findings for <strong>Cross-Module Integrity</strong> only.
Findings highlight potential sequencing, lifecycle, and dataset-alignment issues across related payroll records.
They are integrity indicators and do <strong>not</strong> on their own confirm non-compliance or incorrect pay outcomes.
""".strip()

    cards = [render_cross_finding_card(f) for f in findings]
    return intro + "\n\n" + "\n\n".join(cards)


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

    logo_path = (
        Path(__file__).resolve().parents[1] / "assets" / "crc_logo_full.png"
    ).as_uri()

    parts: List[str] = []
    parts.append(
        build_cover_page(
            report_title="Cross-Module Integrity",
            organisation_name=organisation_name,
            review_period=review_period,
            logo_path=logo_path,
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