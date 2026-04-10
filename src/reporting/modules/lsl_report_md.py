from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from html import escape
from pathlib import Path
from typing import Dict, List, Optional

from reporting.core.structure import ReportStructure
from reporting.executive.exec_pack_md import (
    MODULE_LSL,
    MODULE_LABELS,
    MODULE_ORDER,
    OUTPUTS_DIR,
    build_header,
    build_data_sources_section,
    load_lsl_severity_counts,
)

from reporting.sections.exec_pack_sections import (
    build_scope_and_methodology,
    build_limitations,
    build_next_steps,
    build_appendices,
    build_lsl_severity_summary,
    build_finding_meta,
)

from reporting.core.cover_page import build_cover_page


@dataclass
class LSLFinding:
    rule_code: str
    severity: str
    employee_id: str
    message: str
    classification: str | None = None
    leave_type: str | None = None
    as_of_date: str | None = None
    evidence: str | None = None
    finding_id: str | None = None
    next_action: str | None = None
    diff_units: float | None = None

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "LSLFinding":
        diff_units_raw = row.get("diff_units")
        diff_units: float | None = None
        if diff_units_raw not in (None, ""):
            try:
                diff_units = float(diff_units_raw)
            except ValueError:
                diff_units = None

        return cls(
            rule_code=row.get("rule_code") or row.get("rule_id") or "",
            severity=(row.get("severity") or "").upper(),
            employee_id=row.get("employee_id", ""),
            message=row.get("message") or row.get("description") or "",
            classification=(row.get("classification") or "").upper() or None,
            leave_type=row.get("leave_type") or None,
            as_of_date=row.get("as_of_date") or row.get("snapshot_date") or None,
            evidence=row.get("evidence") or row.get("evidence_ref") or None,
            finding_id=row.get("finding_id") or None,
            next_action=row.get("next_action") or None,
            diff_units=diff_units,
        )


@dataclass
class LSLExposureRow:
    label: str
    amount: float

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> Optional["LSLExposureRow"]:
        label = row.get("label") or row.get("bucket") or row.get("rule_code") or ""
        amount_field_candidates = [
            "estimated_exposure",
            "exposure_amount",
            "lsl_liability",
            "amount",
            "value",
        ]

        amount_value: Optional[float] = None
        for field in amount_field_candidates:
            if field in row and row[field]:
                try:
                    amount_value = float(row[field])
                    break
                except ValueError:
                    continue

        if amount_value is None:
            return None

        return cls(label=label, amount=amount_value)


def _load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_lsl_findings(base_output_dir: Path) -> List[LSLFinding]:
    rows = _load_csv(base_output_dir / "lsl_findings.csv")
    return [LSLFinding.from_row(r) for r in rows]


def load_lsl_exposure_rows(base_output_dir: Path) -> List[LSLExposureRow]:
    rows = _load_csv(base_output_dir / "lsl_exposure_report.csv")
    exposure_rows: List[LSLExposureRow] = []
    for r in rows:
        er = LSLExposureRow.from_row(r)
        if er is not None:
            exposure_rows.append(er)
    return exposure_rows


def _derive_review_period_from_window(data_window_csv: Path) -> str:
    if not data_window_csv.exists():
        return "Review period not clearly identifiable from supplied data"

    rows = _load_csv(data_window_csv)
    if not rows:
        return "Review period not clearly identifiable from supplied data"

    row = rows[0]
    start_raw = (row.get("first_date") or row.get("start_date") or "").strip()
    end_raw = (row.get("last_date") or row.get("end_date") or "").strip()

    if not start_raw or not end_raw:
        return "Review period not clearly identifiable from supplied data"

    try:
        start = date.fromisoformat(start_raw)
        end = date.fromisoformat(end_raw)
    except ValueError:
        return "Review period not clearly identifiable from supplied data"

    if start == end:
        return start.strftime("%d %b %Y")

    return f"{start:%d %b %Y} to {end:%d %b %Y}"


def sort_lsl_findings(findings: List[LSLFinding]) -> List[LSLFinding]:
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(
        findings,
        key=lambda f: (
            severity_rank.get(f.severity, 99),
            f.rule_code or "",
            f.employee_id or "",
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


def render_lsl_finding_card(f: LSLFinding) -> str:
    severity = (f.severity or "").upper() or "INFO"
    severity_class = _severity_class(severity)

    rule_code = escape(f.rule_code or "UNSPECIFIED RULE")
    message = escape(f.message or "No description provided.")
    recommendation_text = f.next_action or (
        "Review the underlying LSL balance, service history and entitlement settings for the affected employee, "
        "confirm whether the balance aligns with applicable rules, and correct any confirmed configuration or data issues."
    )

    extra_parts: list[str] = []
    if f.diff_units is not None:
        if float(f.diff_units).is_integer():
            diff_display = str(int(f.diff_units))
        else:
            diff_display = f"{f.diff_units:.2f}"
        extra_parts.append(f"Variance: {diff_display} units")

    meta_text = build_finding_meta(
        employee_id=f.employee_id or None,
        context_label="Leave type",
        context_value=f.leave_type or None,
        date_label="As at",
        date_value=f.as_of_date or None,
        classification=f.classification or None,
        extra_parts=extra_parts or None,
    )

    impact = (
        "This may indicate a potential misstatement of Long Service Leave entitlements or provisions. "
        "Depending on the nature of the issue, this could affect employee balances and the reliability "
        "of reported LSL exposure."
    )

    sections: list[str] = [
        _render_labeled_section("Finding", message, "finding-main"),
        _render_labeled_section("Impact", escape(impact), "finding-impact"),
        _render_labeled_section("Recommendation", escape(recommendation_text), "finding-action"),
    ]

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


def build_lsl_module_summary(findings: List[LSLFinding]) -> str:
    total_findings = len(findings)
    high = sum(1 for f in findings if f.severity == "HIGH")
    med = sum(1 for f in findings if f.severity == "MEDIUM")
    low = sum(1 for f in findings if f.severity == "LOW")

    distinct_employees = len({f.employee_id for f in findings if f.employee_id})

    paragraph = (
        f"This Long Service Leave (LSL) report focuses solely on LSL-related risk indicators "
        f"identified from the supplied payroll and HR data. A total of {total_findings} potential "
        f"issues were identified across approximately {distinct_employees} employees. These findings "
        "range from likely LSL under- or over-provisioning risk through to data and configuration "
        "issues that may affect the reliability of reported LSL liabilities."
    )

    lines: List[str] = []
    lines.append(paragraph)
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


def build_lsl_detailed_findings(findings: List[LSLFinding]) -> str:
    if not findings:
        return """
<div class="no-findings">
No LSL-related findings were identified for the supplied data.
</div>
""".strip()

    intro = """
This section sets out detailed findings for <strong>Long Service Leave (LSL)</strong> only.
Findings highlight potential inconsistencies, configuration issues, or balance risks that may
affect the reliability of reported LSL entitlements and provisions.
""".strip()

    cards = [render_lsl_finding_card(f) for f in findings]
    return intro + "\n\n" + "\n\n".join(cards)


def build_lsl_exposure_section(exposure_rows: List[LSLExposureRow]) -> str:
    if not exposure_rows:
        return """No LSL exposure estimates were available from the current data extract. If required, aggregated LSL exposure figures can be added to this section in future runs.

---

"""

    total = sum(r.amount for r in exposure_rows)
    lines = [
        f"- Number of exposure rows: {len(exposure_rows)}",
        f"- Indicative total LSL exposure (all categories): {total:,.2f}",
        "",
        "> These figures are indicative only and rely on the provided data and simplifying assumptions. "
        "They do not replace formal actuarial or accounting assessments.",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def build_lsl_appendices(base_output_dir: Path) -> str:
    return build_appendices({MODULE_LSL}, base_output_dir)


def generate_lsl_exposure_report(
    organisation_name: str = "Organisation not specified",
    review_period: Optional[str] = None,
    output_dir: Path | None = None,
) -> Path:
    target_dir = output_dir or OUTPUTS_DIR
    report_path = target_dir / "lsl_report.md"
    lsl_data_window_csv = target_dir / "lsl_data_window.csv"

    raw_findings = load_lsl_findings(target_dir)
    findings = sort_lsl_findings(raw_findings)
    exposure_rows = load_lsl_exposure_rows(target_dir)
    lsl_counts = load_lsl_severity_counts(target_dir)

    if review_period is None:
        review_period = _derive_review_period_from_window(lsl_data_window_csv)

    logo_path = (
        Path(__file__).resolve().parents[1] / "assets" / "crc_logo_full.png"
    ).as_uri()

    parts = [
        build_cover_page(
            report_title="Long Service Leave (LSL) Exposure Review",
            organisation_name=organisation_name,
            review_period=review_period,
            logo_path=logo_path,
        )
    ]

    structure = ReportStructure()
    structure.add("Executive Summary", 1, build_lsl_module_summary(findings))
    structure.add("Data Sources", 1, build_data_sources_section({MODULE_LSL}, target_dir))
    structure.add(
        "Scope & Methodology",
        1,
        build_scope_and_methodology({MODULE_LSL}, MODULE_LABELS, MODULE_ORDER),
    )
    structure.add("Findings Overview", 1, build_lsl_severity_summary(lsl_counts))
    structure.add("Detailed Findings", 1, build_lsl_detailed_findings(findings))
    structure.add("Financial Exposure (Indicative)", 1, build_lsl_exposure_section(exposure_rows))
    structure.add("Limitations & Assumptions", 1, build_limitations())
    structure.add("Recommended Next Steps", 1, build_next_steps(target_dir))
    structure.add("Appendices", 1, build_lsl_appendices(target_dir))

    parts.append(structure.render_markdown())

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(parts), encoding="utf-8")
    return report_path