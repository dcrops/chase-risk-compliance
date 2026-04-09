from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional
from html import escape

from reporting.core.structure import ReportStructure
from reporting.executive.exec_pack_md import (
    MODULE_TERM,
    MODULE_LABELS,
    MODULE_ORDER,
    OUTPUTS_DIR,
    sort_findings,
    build_header,
    build_data_sources_section,
    load_term_severity_counts,
)

from reporting.sections.exec_pack_sections import (
    build_scope_and_methodology,
    build_limitations,
    build_next_steps,
    build_appendices,
    build_term_severity_summary,
)


@dataclass
class TerminationFinding:
    rule_code: str
    severity: str
    employee_id: str
    termination_date: str
    final_pay_date: str
    message: str
    evidence: str | None = None
    days_gap: str | None = None

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "TerminationFinding":
        return cls(
            rule_code=row.get("rule_code") or row.get("rule_id") or "",
            severity=(row.get("severity", "") or "").upper(),
            employee_id=row.get("employee_id", "") or row.get("employee", "") or "",
            termination_date=row.get("termination_date", "") or row.get("term_date", "") or "",
            final_pay_date=row.get("final_pay_date", "") or row.get("pay_date", "") or "",
            message=row.get("message") or row.get("description") or "",
            evidence=row.get("evidence") or row.get("evidence_ref") or row.get("artefact") or None,
            days_gap=row.get("days_gap") or row.get("gap_days") or None,
        )


def _load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []

    import csv

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_term_findings(base_output_dir: Path) -> List[TerminationFinding]:
    rows = _load_csv(base_output_dir / "term_findings.csv")
    return [TerminationFinding.from_row(r) for r in rows]


def _parse_iso_date(s: str | None) -> Optional[date]:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _derive_review_period(findings: List[TerminationFinding]) -> str:
    dates: List[date] = []

    for f in findings:
        d = _parse_iso_date(f.termination_date) or _parse_iso_date(f.final_pay_date)
        if d is not None:
            dates.append(d)

    if not dates:
        return "Review period not clearly identifiable from supplied data"

    start = min(dates)
    end = max(dates)

    if start == end:
        return start.strftime("%d %b %Y")

    return f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"


def _term_severity_class(severity: str) -> str:
    sev = (severity or "").strip().lower()
    if sev in {"high", "medium", "low", "info"}:
        return sev
    return "info"


def _safe(value: str | None, fallback: str = "Not specified") -> str:
    text = (value or "").strip()
    return escape(text) if text else fallback


def render_term_finding_card(finding: TerminationFinding) -> str:
    severity = (finding.severity or "").upper() or "INFO"
    severity_class = _term_severity_class(severity)

    rule_code = _safe(finding.rule_code, "TERM finding")
    employee_id = _safe(finding.employee_id)
    termination_date = _safe(finding.termination_date)
    final_pay_date = _safe(finding.final_pay_date)
    message = _safe(finding.message, "No finding description provided.")
    days_gap = _safe(finding.days_gap, "")
    evidence = _safe(finding.evidence, "")

    meta_parts = [f"Employee: {employee_id}"]

    if termination_date != "Not specified":
        meta_parts.append(f"Termination date: {termination_date}")

    if final_pay_date != "Not specified":
        meta_parts.append(f"Final pay date: {final_pay_date}")

    meta_text = " | ".join(meta_parts)

    impact = (
        "This may weaken the organisation’s ability to clearly evidence termination processing "
        "and final pay handling if reviewed."
    )

    recommendation = (
        "Review the underlying termination workflow, confirm the relevant records and timing, "
        "and validate whether additional supporting evidence or remediation is required."
    )

    extra_sections: list[str] = []

    if days_gap:
        extra_sections.append(
            f'<div class="finding-section"><strong>Timing detail:</strong> Days between termination and final pay: {days_gap}</div>'
        )

    if evidence:
        extra_sections.append(
            f'<div class="finding-section"><strong>Evidence reference</strong></div>'
            f'<pre class="finding-evidence">{evidence}</pre>'
        )

    extra_html = "\n  ".join(extra_sections)

    return f"""
<div class="finding {severity_class}">
  <div class="finding-header">
    <div class="finding-title-wrap">
        <div class="finding-title">{rule_code}</div>
        <div class="finding-meta">{meta_text}</div>
    </div>
    <div class="finding-badge-wrap">
        <span class="badge-{severity_class}">{severity}</span>
    </div>
    </div>

  <div class="finding-section"><strong>Finding:</strong> {message}</div>
  <div class="finding-section"><strong>Impact:</strong> {escape(impact)}</div>
  <div class="finding-section"><strong>Recommendation:</strong> {escape(recommendation)}</div>
  {extra_html}
</div>
""".strip()


def build_term_module_summary(findings: List[TerminationFinding]) -> str:
    parts: List[str] = []

    parts.append(
        "This Termination Exposure report focuses solely on termination-related evidential "
        "risk indicators identified from the supplied payroll and HR data. "
        "The review assesses how complete, timely and traceable termination records appear "
        "for audit and dispute purposes. It does **not** determine whether termination "
        "payments are correct under applicable awards, agreements or contracts."
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


def build_detailed_findings(findings: List[TerminationFinding]) -> str:
    if not findings:
        return """
<div class="no-findings">
No termination-related findings were identified for the supplied data.
</div>
""".strip()

    intro = """
This section sets out detailed findings for **Termination Exposure** only. Findings highlight where termination records may be incomplete, inconsistent or difficult to substantiate if reviewed by auditors, regulators or in the context of a dispute. They do **not** confirm incorrect pay outcomes.
""".strip()

    cards = [render_term_finding_card(f) for f in findings]
    return intro + "\n\n" + "\n\n".join(cards)


def build_term_appendices(base_output_dir: Path) -> str:
    return build_appendices({MODULE_TERM}, base_output_dir)


def generate_term_report(
    organisation_name: str = "Organisation not specified",
    review_period: str | None = None,
    output_dir: Path | None = None,
) -> Path:
    target_dir = output_dir or OUTPUTS_DIR
    report_path = target_dir / "term_report.md"

    findings = load_term_findings(target_dir)
    sorted_findings = sort_findings(findings) if findings else []
    term_counts = load_term_severity_counts(target_dir)

    if review_period is None:
        review_period = _derive_review_period(sorted_findings) if sorted_findings else "Period not specified"

    parts: List[str] = []
    parts.append(
        build_header(
            "Termination Exposure – Detailed Report",
            organisation_name,
            review_period,
        )
    )

    structure = ReportStructure()
    structure.add("Executive Summary", 1, build_term_module_summary(sorted_findings))
    structure.add("Data Sources", 1, build_data_sources_section({MODULE_TERM}, target_dir))
    structure.add(
        "Scope & Methodology",
        1,
        build_scope_and_methodology({MODULE_TERM}, MODULE_LABELS, MODULE_ORDER),
    )
    structure.add("Findings Overview", 1, build_term_severity_summary(term_counts))
    structure.add("Detailed Findings", 1, build_detailed_findings(sorted_findings))
    structure.add("Limitations & Assumptions", 1, build_limitations())
    structure.add("Recommended Next Steps", 1, build_next_steps(target_dir))
    structure.add("Appendices", 1, build_term_appendices(target_dir))

    parts.append(structure.render_markdown())
    final_md = "\n".join(parts)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(final_md, encoding="utf-8")
    return report_path