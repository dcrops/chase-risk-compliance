from __future__ import annotations

import csv
from datetime import date
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
)


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

    parts: List[str] = []
    parts.append(
        build_header(
            "Leave & Entitlement Leakage – Detailed Report",
            organisation_name,
            review_period,
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
        return """No findings were identified for the supplied data.

---

"""

    lines: List[str] = []

    lines.append(
        "This section sets out detailed findings for **leave and entitlement leakage** only. "
        "Record-Keeping & Evidence Gaps (RKEG) and Termination Exposure findings are available "
        "in machine-readable form (see Appendix C) and are intended to support operational review, "
        "sampling and remediation planning rather than narrative reporting."
    )
    lines.append("")
    lines.append(
        "Each leave finding below follows a consistent **Finding → Evidence → Impact → Recommended Action** pattern."
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

        evidence_bits = []
        if f.employee_id:
            evidence_bits.append(f"Employee ID: `{f.employee_id}`")
        if f.leave_type:
            evidence_bits.append(f"Leave type: `{f.leave_type}`")
        if f.as_of_date:
            evidence_bits.append(f"As at: `{f.as_of_date}`")

        if evidence_bits:
            lines.append("- " + "\n- ".join(evidence_bits))
        else:
            lines.append("- Not specified in the source data.")
        lines.append("")
        lines.append("**Impact / Risk**")
        lines.append(
            "Potential leave or entitlement imbalance and/or record-keeping weakness. "
            "The actual impact will depend on the underlying award or agreement, "
            "actual pay outcomes, and the period over which the issue has occurred."
        )
        lines.append("")
        lines.append("**Recommended Action**")
        lines.append("")
        lines.append("- Validate this finding against source payroll records and employee entitlements.")
        lines.append("- Correct any confirmed configuration, data or process issues.")
        lines.append("- Consider remediation where underpayments are confirmed.")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


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