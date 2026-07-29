from __future__ import annotations

import csv
from datetime import date
from html import escape
from pathlib import Path
from typing import List

from reporting.leave_common import (
    Finding,
    ExposureRow,
    derive_leave_review_period,
)

from reporting.core.structure import ReportStructure
from reporting.executive.exec_pack_md import (
    MODULE_LEAVE,
    OUTPUTS_DIR,
    MODULE_ORDER,
    MODULE_LABELS,
    sort_findings,
    build_header,
    build_data_sources_section,
    build_key_findings_overview,
)

from reporting.sections.exec_pack_sections import (
    build_scope_and_methodology,
    build_limitations,
    build_next_steps,
    build_appendices,
    build_finding_meta,
)

from reporting.core.cover_page import build_cover_page


def _load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def load_leave_findings(base_output_dir: Path) -> List[Finding]:
    rows = _load_csv(base_output_dir / "leave_leakage_findings.csv")
    return [Finding.from_row(r) for r in rows]


def load_leave_exposure_rows(base_output_dir: Path) -> List[ExposureRow]:
    rows = _load_csv(base_output_dir / "leakage_report.csv")
    exposure_rows: List[ExposureRow] = []
    for r in rows:
        er = ExposureRow.from_row(r)
        if er is not None:
            exposure_rows.append(er)
    return exposure_rows


def _derive_review_period_from_window(path: Path) -> str | None:
    if not path.exists():
        return None

    try:
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except OSError:
        return None

    if not rows:
        return None

    row = rows[0]
    start_raw = (row.get("first_date") or row.get("start_date") or "").strip()
    end_raw = (row.get("last_date") or row.get("end_date") or "").strip()
    if not start_raw:
        return None

    try:
        start = date.fromisoformat(start_raw)
        end = date.fromisoformat(end_raw) if end_raw else start
    except ValueError:
        return None

    if start == end:
        return start.strftime("%d %b %Y")
    return f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"


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


def render_leave_finding_card(f: Finding) -> str:
    severity = (getattr(f, "severity", "") or "").upper() or "INFO"
    severity_class = _severity_class(severity)

    rule_code = escape(getattr(f, "rule_code", "") or "UNSPECIFIED RULE")
    message = escape(getattr(f, "message", "") or "No description provided.")

    evidence = getattr(f, "evidence", None)
    recommendation_text = getattr(f, "next_action", None) or (
        "Validate the finding against source payroll records and employee entitlements, "
        "correct any confirmed configuration, data or process issues, and consider remediation "
        "where underpayments are confirmed."
    )

    diff_units = getattr(f, "diff_units", None)
    extra_parts: list[str] = []
    if diff_units is not None and str(diff_units).strip() != "":
        try:
            diff_value = float(diff_units)
            if diff_value.is_integer():
                diff_display = str(int(diff_value))
            else:
                diff_display = f"{diff_value:.2f}"
        except (TypeError, ValueError):
            diff_display = str(diff_units)

        extra_parts.append(f"Variance: {diff_display} units")

    meta_text = build_finding_meta(
        employee_id=getattr(f, "employee_id", "") or None,
        context_label="Leave type",
        context_value=getattr(f, "leave_type", "") or None,
        date_label="As at",
        date_value=getattr(f, "as_of_date", "") or None,
        classification=getattr(f, "classification", None),
        extra_parts=extra_parts or None,
    )

    impact = (
        "This may indicate leave balance inaccuracies, accrual miscalculations, or record-keeping gaps. "
        "The actual impact depends on the underlying configuration, employee history, and duration of the issue."
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
            + escape(evidence)
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


def build_leave_module_summary(
    findings: List[Finding],
    exposure_rows: List[ExposureRow],
) -> str:
    parts: List[str] = []

    parts.append(
        "This Leave & Entitlement Leakage report focuses solely on leave-related risk "
        "indicators identified from the supplied payroll and HR data. "
        "Findings are risk indicators only and do not, on their own, confirm underpayment, "
        "non-compliance, or an entitlement error."
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
    parts.append("")
    parts.append(build_financial_exposure_section(exposure_rows))

    return "\n".join(parts).strip()


def build_leave_appendices(base_output_dir: Path) -> str:
    return build_appendices({MODULE_LEAVE}, base_output_dir)


def generate_leave_report(
    organisation_name: str = "Organisation not specified",
    review_period: str | None = None,
    output_dir: Path | None = None,
) -> Path:
    target_dir = output_dir or OUTPUTS_DIR
    report_path = target_dir / "leave_report.md"
    leave_data_window_csv = target_dir / "leave_data_window.csv"

    findings = load_leave_findings(target_dir)
    sorted_findings = sort_findings(findings) if findings else []
    exposure_rows = load_leave_exposure_rows(target_dir)

    if review_period is None:
        from_window = _derive_review_period_from_window(leave_data_window_csv)

        if from_window is not None:
            review_period = from_window
        else:
            review_period = (
                derive_leave_review_period(sorted_findings)
                if sorted_findings
                else "Review period not clearly identifiable from supplied data"
            )

    logo_path = (
        Path(__file__).resolve().parents[1] / "assets" / "crc_logo_full.png"
    ).as_uri()

    parts: List[str] = []
    parts.append(
        build_cover_page(
            report_title="Leave & Entitlement Leakage",
            organisation_name=organisation_name,
            review_period=review_period,
            logo_path=logo_path,
        )
    )

    structure = ReportStructure()
    structure.add(
        "Executive Summary",
        1,
        build_leave_module_summary(sorted_findings, exposure_rows),
    )
    structure.add(
        "Data Sources",
        1,
        build_data_sources_section({MODULE_LEAVE}, target_dir),
    )
    structure.add(
        "Scope & Methodology",
        1,
        build_scope_and_methodology({MODULE_LEAVE}, MODULE_LABELS, MODULE_ORDER),
    )
    structure.add(
        "Findings Overview",
        1,
        build_key_findings_overview(sorted_findings),
    )
    structure.add(
        "Detailed Findings",
        1,
        build_detailed_findings(sorted_findings),
    )
    structure.add(
        "Financial Exposure (Indicative)",
        1,
        build_financial_exposure_section(exposure_rows),
    )
    structure.add(
        "Limitations & Assumptions",
        1,
        build_limitations(),
    )
    structure.add(
        "Recommended Next Steps",
        1,
        build_next_steps(target_dir),
    )
    structure.add(
        "Appendices",
        1,
        build_leave_appendices(target_dir),
    )

    parts.append(structure.render_markdown())
    final_md = "\n".join(parts)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(final_md, encoding="utf-8")
    return report_path


def build_detailed_findings(findings: List[Finding]) -> str:
    if not findings:
        return """
<div class="no-findings">
No findings were identified for the supplied data.
</div>
""".strip()

    intro = """
This section sets out detailed findings for <strong>Leave &amp; Entitlement Leakage</strong> only.
Findings highlight potential leave balance inconsistencies, accrual issues, or record weaknesses.
They are risk indicators only and do <strong>not</strong> confirm underpayment, non-compliance, or an entitlement error.
""".strip()

    cards = [render_leave_finding_card(f) for f in findings]
    return intro + "\n\n" + "\n\n".join(cards)


def build_financial_exposure_section(exposure_rows: List[ExposureRow]) -> str:
    if not exposure_rows:
        return """No exposure estimates were available from the current data extract. If required, leakage estimates can be added to this section in future runs.

---

"""

    total = sum(r.amount for r in exposure_rows)

    lines = [
        f"- Number of findings with exposure estimates: {len(exposure_rows)}",
        f"- Indicative total exposure (all severities): {total:,.2f}",
        "",
        "> These figures are indicative only and rely on the provided data and simplifying assumptions. "
        "They should be validated before any remediation or accounting decisions are made.",
        "",
        "---",
        "",
    ]

    return "\n".join(lines)