from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Optional
from html import escape

from reporting.core.review_period import derive_review_period_from_windows
from reporting.core.structure import ReportStructure
from reporting.executive.exec_pack_md import (
    MODULE_RKEG,
    MODULE_LABELS,
    MODULE_ORDER,
    OUTPUTS_DIR,
    sort_findings,
    build_header,
    build_data_sources_section,
    load_rkeg_severity_counts,
)

from reporting.sections.exec_pack_sections import (
    build_scope_and_methodology,
    build_limitations,
    build_next_steps,
    build_appendices,
    build_rkeg_summary,
    build_finding_meta,
)

from reporting.core.cover_page import build_cover_page

@dataclass
class RKEGFinding:
    rule_code: str
    severity: str
    employee_id: str
    leave_type: str
    as_of_date: str
    message: str
    classification: str | None = None
    evidence: Optional[str] = None
    finding_id: Optional[str] = None
    next_action: Optional[str] = None

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "RKEGFinding":
        return cls(
            rule_code=row.get("rule_code") or row.get("rule_id") or "",
            severity=(row.get("severity", "") or "").upper(),
            employee_id=row.get("employee_id", "") or row.get("employee", "") or "",
            leave_type=row.get("leave_type", "") or row.get("record_type", "") or "",
            as_of_date=row.get("as_of_date", "") or row.get("snapshot_date", "") or "",
            message=row.get("message") or row.get("description") or "",
            classification=(row.get("classification") or "").upper() or None,
            evidence=row.get("evidence") or row.get("evidence_ref") or None,
            finding_id=row.get("finding_id") or None,
            next_action=row.get("next_action") or None,
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


def _safe(value: str | None, fallback: str = "Not specified") -> str:
    text = (value or "").strip()
    return escape(text) if text else fallback


def _render_labeled_section(label: str, body: str, extra_class: str = "") -> str:
    class_attr = f"finding-text {extra_class}".strip()
    return f"""
<div class="finding-section">
  <div class="finding-label">{escape(label)}</div>
  <div class="{class_attr}">{body}</div>
</div>
""".strip()


def render_rkeg_finding_card(f: RKEGFinding) -> str:
    severity_class = _severity_class(f.severity)
    severity = (f.severity or "").upper() or "INFO"

    rule_code = _safe(f.rule_code, "UNSPECIFIED RULE")
    message = _safe(f.message, "No description provided.")
    evidence = _safe(f.evidence, "")
    recommendation_text = f.next_action or (
        "Validate the underlying records, ensure key identifiers and dates are consistently captured, "
        "and strengthen documentation and data capture processes where patterns are identified."
    )

    meta_text = build_finding_meta(
        employee_id=f.employee_id or None,
        context_label="Record type",
        context_value=f.leave_type or None,
        date_label="As at",
        date_value=f.as_of_date or None,
        classification=f.classification or None,
    )

    impact = (
        "This may increase evidential and audit risk in relation to payroll records. "
        "Weak, incomplete or inconsistent records can reduce the organisation's ability "
        "to respond confidently if challenged."
    )

    sections: list[str] = [
        _render_labeled_section("Finding", message, "finding-main"),
        _render_labeled_section("Impact", escape(impact), "finding-impact"),
        _render_labeled_section("Recommendation", escape(recommendation_text), "finding-action"),
    ]

    if evidence:
        sections.append(
            """
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">"""
            + evidence
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
      <span class="badge-{severity_class}">{severity}</span>
    </div>
  </div>

  <div class="finding-meta">{meta_text}</div>

  {section_html}
</div>
""".strip()


def _load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    import csv

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_rkeg_findings(base_output_dir: Path) -> List[RKEGFinding]:
    rows = _load_csv(base_output_dir / "rkeg_findings.csv")
    return [RKEGFinding.from_row(r) for r in rows]


def _parse_iso_date(s: str | None) -> Optional[date]:
    if not s:
        return None

    value = s.strip()
    if not value:
        return None

    if value.lower() in {"n/a", "na", "none", "null", "unknown", "-"}:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            parsed = datetime.strptime(value, fmt).date()
        except ValueError:
            continue

        today = date.today()
        if parsed.year < 2000 or parsed.year > today.year + 1:
            return None

        return parsed

    return None


def _derive_review_period(findings: List[RKEGFinding], data_window_csv: Path) -> str:
    period_from_window = derive_review_period_from_windows(
        [data_window_csv],
        fallback=None,
    )
    if period_from_window:
        return period_from_window

    dates: List[date] = []
    for f in findings:
        d = _parse_iso_date(f.as_of_date)
        if d is not None:
            dates.append(d)

    if not dates:
        return "Period not specified"

    start = min(dates)
    end = max(dates)

    if start == end:
        return start.strftime("%d %b %Y")

    return f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"


def build_rkeg_module_summary(findings: List[RKEGFinding]) -> str:
    parts: List[str] = []

    parts.append(
        "This Record-Keeping & Evidence Gaps (RKEG) report focuses solely on evidential "
        "risk indicators identified from the supplied payroll and HR data. "
        "The review assesses how complete, consistent and traceable payroll-related records "
        "appear for audit and dispute purposes. It does **not** determine whether payroll "
        "outcomes are correct or incorrect under applicable legislation, awards or agreements."
    )
    parts.append("")

    high = sum(1 for f in findings if f.severity == "HIGH")
    med = sum(1 for f in findings if f.severity == "MEDIUM")
    low = sum(1 for f in findings if f.severity == "LOW")

    parts.append("Across the dataset provided, the automated checks identified:")
    parts.append("")
    parts.append(f"- **High:** {high}")
    parts.append(f"- **Medium:** {med}")
    parts.append(f"- **Low:** {low}")
    parts.append("")
    parts.append(
        "A detailed breakdown by severity is provided in the "
        "**Findings Overview** section."
    )

    return "\n".join(parts).strip()


def build_rkeg_findings_overview(base_output_dir: Path) -> str:
    counts = load_rkeg_severity_counts(base_output_dir)
    return build_rkeg_summary(counts)


def build_detailed_findings(findings: List[RKEGFinding]) -> str:
    if not findings:
        return """
<div class="no-findings">
No record-keeping or evidence gaps were identified for the supplied data.
</div>
""".strip()

    intro = """
This section sets out detailed findings for <strong>Record-Keeping &amp; Evidence Gaps (RKEG)</strong> only.
Findings highlight where payroll-related records may be incomplete, inconsistent or difficult
to substantiate if reviewed by auditors, regulators or in the context of a dispute.
They do <strong>not</strong> confirm incorrect pay outcomes.
""".strip()

    cards = [render_rkeg_finding_card(f) for f in findings]

    return intro + "\n\n" + "\n\n".join(cards)


def build_rkeg_appendices(base_output_dir: Path) -> str:
    return build_appendices({MODULE_RKEG}, base_output_dir)


def generate_rkeg_report(
    organisation_name: str = "Organisation not specified",
    review_period: str | None = None,
    output_dir: Path | None = None,
) -> Path:
    target_dir = output_dir or OUTPUTS_DIR
    report_path = target_dir / "rkeg_report.md"
    rkeg_data_window_csv = target_dir / "rkeg_data_window.csv"

    findings = load_rkeg_findings(target_dir)
    sorted_findings = sort_findings(findings) if findings else []

    if review_period is None:
        review_period = (
            _derive_review_period(sorted_findings, rkeg_data_window_csv)
            if sorted_findings
            else "Period not specified"
        )

    logo_path = (
        Path(__file__).resolve().parents[1] / "assets" / "crc_logo_full.png"
    ).as_uri()

    parts: List[str] = []
    parts.append(
        build_cover_page(
            report_title="Record-Keeping & Evidence Gaps (RKEG)",
            organisation_name=organisation_name,
            review_period=review_period,
            logo_path=logo_path,
        )
    )

    structure = ReportStructure()
    structure.add("Executive Summary", 1, build_rkeg_module_summary(sorted_findings))
    structure.add("Data Sources", 1, build_data_sources_section({MODULE_RKEG}, target_dir))
    structure.add(
        "Scope & Methodology",
        1,
        build_scope_and_methodology({MODULE_RKEG}, MODULE_LABELS, MODULE_ORDER),
    )
    structure.add("Findings Overview", 1, build_rkeg_findings_overview(target_dir))
    structure.add("Detailed Findings", 1, build_detailed_findings(sorted_findings))
    structure.add("Limitations & Assumptions", 1, build_limitations())
    structure.add("Recommended Next Steps", 1, build_next_steps(target_dir))
    structure.add("Appendices", 1, build_rkeg_appendices(target_dir))

    parts.append(structure.render_markdown())
    final_md = "\n".join(parts)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(final_md, encoding="utf-8")
    return report_path