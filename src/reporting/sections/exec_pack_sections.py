from __future__ import annotations

from pathlib import Path
from typing import List, Dict
from html import escape


# ======================================
# Scope Intro
# ======================================

def build_scope_intro(module_labels: dict, ordered_modules: list[str]) -> str:
    lines: List[str] = []
    lines.append("**Modules included in this engagement:**")
    lines.append("")

    for m in ordered_modules:
        lines.append(f"- {module_labels[m]}")

    if not ordered_modules:
        lines.append("- None specified")

    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def build_scope_and_methodology(
    included_modules: set[str] | list[str] | None,
    module_labels: dict[str, str],
    module_order: list[str],
) -> str:
    mods = {m.strip().upper() for m in (included_modules or [])}
    ordered = [m for m in module_order if m in mods]

    lines: List[str] = []
    lines.append(build_scope_intro(module_labels, ordered))

    if "LEAVE" in mods:
        lines.append("### **Leave & Entitlement Leakage – Scope & Methodology**")
        lines.append("")
        lines.append(build_scope_leave())

    if "LSL" in mods:
        lines.append("### **Long Service Leave (LSL) Exposure – Scope & Methodology**")
        lines.append("")
        lines.append(build_scope_lsl())

    if "TERM" in mods:
        lines.append("### **Termination Exposure – Scope & Methodology**")
        lines.append("")
        lines.append(build_scope_term())

    if "RKEG" in mods:
        lines.append("### **Record-Keeping & Evidence Gaps (RKEG) – Scope & Methodology**")
        lines.append("")
        lines.append(build_scope_rkeg())

    if "CROSS_MODULE" in mods:
        lines.append("### **Cross-Module Integrity – Scope & Methodology**")
        lines.append("")
        lines.append(build_scope_cross_module())

    if not mods:
        lines.append("No scoped modules were included in this run.")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

# ======================================
# Scope Sections
# ======================================

def build_scope_leave() -> str:
    lines: List[str] = []
    lines.append("**Scope**")
    lines.append("")
    lines.append(
        "The Leave & Entitlement Leakage review identifies potential anomalies and risk indicators in leave balances, accruals and leave usage based on the data provided."
    )
    lines.append("")
    lines.append(
        "The purpose of this review is to highlight records that may warrant follow-up, such as negative balances, unexpected accrual patterns, mismatches between leave activity and employee status, or inconsistencies between leave movement data and balance snapshots."
    )
    lines.append("")
    lines.append(
        "This review is designed to support payroll and HR teams in prioritising validation and remediation effort. Findings are risk signals only and do not, on their own, confirm non-compliance, underpayment, or an entitlement error."
    )
    lines.append("")
    lines.append("**Data reviewed**")
    lines.append("")
    lines.append("- leave balances snapshot data (where supplied)")
    lines.append("- leave ledger / leave movement records (where supplied)")
    lines.append("- employee master data (where supplied)")
    lines.append("- other supporting payroll extracts included in the engagement pack")
    lines.append("")
    lines.append("**Checks performed**")
    lines.append("")
    lines.append("- rule-based detection of unusual leave balance and movement patterns")
    lines.append("- identification of negative balances and unexpected accrual behaviour")
    lines.append("- consistency checks between employee status and leave activity (for example, terminated employees with ongoing leave movements)")
    lines.append("- cross-checks between leave movement data and balance snapshot fields where available")
    lines.append("")
    lines.append("**Out of scope**")
    lines.append("")
    lines.append("This review does not:")
    lines.append("")
    lines.append("- interpret awards, enterprise agreements, or employment contracts")
    lines.append("- calculate legal entitlement outcomes or confirm the correctness of leave accrual rules")
    lines.append("- provide legal, accounting, or industrial relations advice")
    lines.append("- assert contraventions of legislation or confirm non-compliance.")
    lines.append("")
    lines.append(
        "Where exposure estimates are included, they are indicative only and must be validated before remediation or accounting decisions are made."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_scope_lsl() -> str:
    lines: List[str] = []
    lines.append("**Scope**")
    lines.append("")
    lines.append(
        "The Long Service Leave (LSL) Exposure review identifies risk indicators in LSL balance and service-related data that may warrant further validation. The purpose of this review is to highlight records that appear inconsistent, incomplete, or difficult to substantiate based on the data provided."
    )
    lines.append("")
    lines.append(
        "This review is designed to support payroll, HR and finance teams in prioritising follow-up effort. Findings are risk signals only and do not, on their own, confirm an entitlement error, underpayment, or non-compliance."
    )
    lines.append("")
    lines.append("**Data reviewed**")
    lines.append("")
    lines.append("- employee master data relevant to LSL service (where supplied)")
    lines.append("- LSL balance snapshot data (where supplied)")
    lines.append("- LSL accrual or movement records (where supplied)")
    lines.append("- other supporting payroll extracts included in the engagement pack")
    lines.append("")
    lines.append("**Checks performed**")
    lines.append("")
    lines.append("- consistency checks between LSL balances, accrual patterns, and available service-related fields")
    lines.append("- identification of missing or incomplete service date records required to support LSL calculations")
    lines.append("- detection of unusual balance or movement patterns that may indicate configuration or data issues")
    lines.append("")
    lines.append("**Out of scope**")
    lines.append("")
    lines.append("This review does not:")
    lines.append("")
    lines.append("- interpret awards, enterprise agreements, or employment contracts")
    lines.append("- calculate legal LSL entitlement outcomes or confirm the correctness of LSL accrual rules")
    lines.append("- provide legal, accounting, or industrial relations advice")
    lines.append("- assert contraventions of legislation or confirm non-compliance.")
    lines.append("")
    lines.append(
        "Where any exposure estimates or balance concerns are inferred, they are indicative only and must be validated before remediation or accounting decisions are made."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_scope_term() -> str:
    lines: List[str] = []
    lines.append("**Scope**")
    lines.append("")
    lines.append(
        "The Termination Exposure review assesses whether termination events recorded in payroll and related employment data are sufficiently complete, timely, and traceable to support the organisation’s ability to evidence termination-related payroll decisions if reviewed by auditors or regulators."
    )
    lines.append("")
    lines.append(
        "This review focuses on process and evidential integrity, not on the correctness of termination payments."
    )
    lines.append("")
    lines.append("Specifically, the review considers whether:")
    lines.append("")
    lines.append("- termination events are recorded consistently across available data sources")
    lines.append("- final pay processing occurs in a reasonable and defensible sequence relative to termination dates")
    lines.append("- core termination attributes (such as termination date and termination type/reason) are present and internally consistent")
    lines.append("- termination-related decisions are supported by basic evidentiary artefacts or references")
    lines.append("")
    lines.append("**Out of scope**")
    lines.append("")
    lines.append("This review does not:")
    lines.append("")
    lines.append("- calculate final pay entitlements or assess payment correctness")
    lines.append("- interpret awards, enterprise agreements, or employment contracts")
    lines.append("- determine notice, redundancy, or severance obligations")
    lines.append("- assert contraventions of legislation or confirm non-compliance.")
    lines.append("- provide legal advice or assurance of compliance.")
    lines.append("")
    lines.append("Any potential exposure identified reflects defensibility risk, not confirmed error or liability.")
    lines.append("")
    lines.append("**Methodology**")
    lines.append("")
    lines.append(
        "The review applies a series of rule-based checks to payroll and related employment data to identify termination events that exhibit characteristics commonly associated with audit, regulatory, or dispute risk."
    )
    lines.append("")
    lines.append(
        "Each finding is assigned a severity based on evidential impact, reflecting how materially the issue could impair the organisation’s ability to explain and support termination-related payroll decisions if reviewed."
    )
    lines.append("")
    lines.append("Severity does not represent:")
    lines.append("")
    lines.append("- likelihood of underpayment")
    lines.append("- magnitude of potential monetary impact")
    lines.append("- remediation priority")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_scope_rkeg() -> str:
    lines: List[str] = []
    lines.append("**Scope**")
    lines.append("")
    lines.append(
        "The Record-Keeping & Evidence Gaps (RKEG) review assesses whether payroll-related records are sufficiently complete, consistent and traceable to support the organisation’s ability to evidence payroll decisions if reviewed by auditors or regulators."
    )
    lines.append("")
    lines.append(
        "RKEG focuses on evidential strength, not on determining whether payroll outcomes are correct or incorrect. Findings highlight where records may be incomplete, inconsistent, or difficult to substantiate if challenged."
    )
    lines.append("")
    lines.append(
        "This review is intended to support risk-aware payroll operations by identifying evidence weaknesses that can increase audit effort, increase dispute risk, or reduce the organisation’s ability to confidently explain pay decisions."
    )
    lines.append("")
    lines.append("**Data reviewed**")
    lines.append("")
    lines.append("- employee master data (where supplied)")
    lines.append("- pay event / payroll transaction extracts (where supplied)")
    lines.append("- termination and employment status fields where included in the engagement data pack")
    lines.append("")
    lines.append("**Checks performed**")
    lines.append("")
    lines.append("- completeness checks for key employee master fields required for traceability and defensibility")
    lines.append("- identification of orphan or untraceable pay events (for example, pay events with missing or inconsistent identifiers)")
    lines.append("- consistency checks across employee status and payroll activity where possible")
    lines.append("- identification of gaps that may require manual reconstruction to support an audit trail")
    lines.append("")
    lines.append("**Out of scope**")
    lines.append("")
    lines.append("This review does not:")
    lines.append("")
    lines.append("- calculate entitlements, underpayments or overpayments")
    lines.append("- interpret awards, enterprise agreements, or employment contracts")
    lines.append("- provide legal, accounting, or industrial relations advice")
    lines.append("- assert contraventions of legislation or confirm non-compliance.")
    lines.append("")
    lines.append(
        "RKEG findings should be interpreted as evidential risk indicators. Addressing them improves defensibility and reduces audit effort, but does not necessarily imply a payroll outcome is incorrect."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_scope_cross_module() -> str:
    lines: List[str] = []
    lines.append("**Scope**")
    lines.append("")
    lines.append(
        "The Cross-Module Integrity review assesses whether related payroll datasets align consistently across employee lifecycle, leave, payroll event, and termination records."
    )
    lines.append("")
    lines.append(
        "The purpose of this review is to identify inconsistencies between linked datasets that may indicate sequencing issues, lifecycle mismatches, incomplete integrations, or broader payroll data integrity weaknesses."
    )
    lines.append("")
    lines.append(
        "This review is designed to support payroll, HR, finance, and governance teams in identifying where records may not align cleanly across the broader payroll data environment. Findings are integrity signals only and do not, on their own, confirm non-compliance, underpayment, or payroll error."
    )
    lines.append("")
    lines.append("**Data reviewed**")
    lines.append("")
    lines.append("- employee master data (where supplied)")
    lines.append("- leave balances and leave movement data (where supplied)")
    lines.append("- payroll event / payroll transaction extracts (where supplied)")
    lines.append("- termination and lifecycle-related records where included in the engagement data pack")
    lines.append("")
    lines.append("**Checks performed**")
    lines.append("")
    lines.append("- consistency checks between employee lifecycle status and payroll activity")
    lines.append("- identification of mismatches between leave activity and termination or employment status")
    lines.append("- cross-dataset linkage checks for related employee and payroll records")
    lines.append("- detection of sequencing anomalies between linked events across modules")
    lines.append("")
    lines.append("**Out of scope**")
    lines.append("")
    lines.append("This review does not:")
    lines.append("")
    lines.append("- calculate entitlements, underpayments or overpayments")
    lines.append("- interpret awards, enterprise agreements, or employment contracts")
    lines.append("- provide legal, accounting, or industrial relations advice")
    lines.append("- assert contraventions of legislation or confirm non-compliance.")
    lines.append("")
    lines.append(
        "Cross-module findings should be interpreted as data integrity and linkage risk indicators. They highlight where records may not align cleanly across datasets and may require investigation before conclusions are drawn."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


# ======================================
# No Findings / Coverage Notes
# ======================================

def _no_findings_block(message: str) -> str:
    return f"""<div class="no-findings">
{message}
</div>

---
""".strip()


def build_leave_no_findings_message(label: str = "leave and entitlement") -> str:
    return _no_findings_block(f"No material {label} findings were identified in the current dataset.")


def build_term_no_findings_message(label: str = "termination-related") -> str:
    return _no_findings_block(f"No material {label} findings were identified in the current dataset.")


def build_rkeg_no_findings_message(label: str = "record-keeping or evidence gap") -> str:
    return _no_findings_block(f"No material {label} findings were identified in the current dataset.")


def build_cross_no_findings_message(label: str = "cross-module integrity") -> str:
    return _no_findings_block(f"No material {label} findings were identified in the current dataset.")


def build_lsl_no_findings_message(label: str = "long service leave") -> str:
    return _no_findings_block(f"No material {label} findings were identified in the current dataset.")


def build_lsl_coverage_note() -> str:
    return """<div class="no-findings">
<strong>Coverage note:</strong><br>
No Long Service Leave (LSL) activity was identified in the dataset provided for this review.

Accordingly, LSL-related diagnostics were not performed.

This reflects a data coverage limitation rather than a confirmed absence of LSL risk. Assessment of LSL exposure typically requires service history, eligibility thresholds, and accrual data that may not be present in payroll-only extracts.
</div>

---
""".strip()

def build_finding_meta(
    *,
    employee_id: str | None = None,
    context_label: str | None = None,
    context_value: str | None = None,
    date_label: str | None = None,
    date_value: str | None = None,
    classification: str | None = None,
    extra_parts: list[str] | None = None,
) -> str:
    parts: list[str] = []

    if employee_id:
        parts.append(f"Employee: {escape(employee_id)}")

    if context_label and context_value:
        parts.append(f"{escape(context_label)}: {escape(context_value)}")

    if date_label and date_value:
        parts.append(f"{escape(date_label)}: {escape(date_value)}")

    if classification:
        parts.append(f"Classification: {escape(classification)}")

    if extra_parts:
        for part in extra_parts:
            if part and part.strip():
                parts.append(escape(part.strip()))

    return " | ".join(parts) if parts else "Reference details not specified"


# ======================================
# Summary Builders
# ======================================

def build_rkeg_summary(rkeg_counts: Dict[str, int]) -> str:
    if not any(rkeg_counts.values()):
        return build_rkeg_no_findings_message("record-keeping and evidence gaps")

    return f"""
As part of this review, a Record-Keeping & Evidence Gaps (RKEG) assessment was performed to evaluate whether payroll-related records are sufficiently complete, consistent and traceable to support payroll decisions if subject to audit or regulatory review.

The RKEG assessment focuses on evidential strength only. It does not determine whether payroll outcomes are correct or incorrect, and does not interpret awards, enterprise agreements or employment contracts.

The table below summarises the number of record-keeping and evidence gaps identified by severity. Counts reflect **evidential risk** only and do not represent confirmed non-compliance or a quantified monetary impact.

<table class="summary-table">
  <thead>
    <tr>
      <th>Severity</th>
      <th>Count</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="badge-high">High</span></td>
      <td>{rkeg_counts["HIGH"]}</td>
      <td>Absence or weakness of core evidence or entitlement configuration that would materially impair the organisation’s ability to evidence payroll decisions if reviewed by auditors or regulators.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>{rkeg_counts["MEDIUM"]}</td>
      <td>Evidence is incomplete, inconsistent or fragile. Decisions may still be defensible but require greater reliance on manual reconstruction, judgement, or explanation.</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>{rkeg_counts["LOW"]}</td>
      <td>Record-keeping or data quality weaknesses that are unlikely to be challenged in isolation but should be improved over time to support efficient and reliable payroll operations.</td>
    </tr>
  </tbody>
</table>

---
""".strip()


def build_lsl_severity_summary(lsl_counts: Dict[str, int]) -> str:
    if not any(lsl_counts.values()):
        return ""

    return f"""Where an LSL Exposure review was performed, the table below summarises the number of LSL-related risk indicators identified by severity. Counts reflect **risk indicators only** and do not represent confirmed underpayments, quantified exposure, or remediation priority.

<table class="summary-table">
  <thead>
    <tr>
      <th>Severity</th>
      <th>Count</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="badge-high">High</span></td>
      <td>{lsl_counts["HIGH"]}</td>
      <td>Indicators likely to require prompt validation due to potential material impact or audit defensibility concerns.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>{lsl_counts["MEDIUM"]}</td>
      <td>Indicators that may reflect configuration, data quality, or timing weaknesses requiring review.</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>{lsl_counts["LOW"]}</td>
      <td>Lower-impact indicators that should be improved over time.</td>
    </tr>
  </tbody>
</table>

---
""".strip()


def build_term_severity_summary(term_counts: Dict[str, int]) -> str:
    if not any(term_counts.values()):
        return build_term_no_findings_message("termination-related")

    return f"""
Where a Termination Exposure review was performed, the table below summarises the number of termination-related evidential issues identified by severity. Counts reflect **evidential risk only** and do not represent confirmed non-compliance, a quantified monetary impact, or remediation priority.

<table class="summary-table">
  <thead>
    <tr>
      <th>Severity</th>
      <th>Count</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="badge-high">High</span></td>
      <td>{term_counts["HIGH"]}</td>
      <td>Absence or weakness of core termination or final pay evidence that would materially impair the organisation’s ability to evidence termination decisions if reviewed by auditors or regulators.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>{term_counts["MEDIUM"]}</td>
      <td>Termination evidence exists but is incomplete, delayed or ambiguous and may require additional explanation or manual reconstruction.</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>{term_counts["LOW"]}</td>
      <td>Minor record-keeping or data quality weaknesses in termination records that should be improved over time to support efficient and reliable payroll operations.</td>
    </tr>
  </tbody>
</table>

---
""".strip()


def build_cross_module_summary(cross_counts: Dict[str, int]) -> str:
    if not any(cross_counts.values()):
        return build_cross_no_findings_message("cross-module integrity")

    return f"""Where a Cross-Module Integrity review was performed, the table below summarises the number of cross-module inconsistencies identified by severity. Counts reflect **integrity risk indicators only** and do not represent confirmed non-compliance or a quantified monetary impact.

<table class="summary-table">
  <thead>
    <tr>
      <th>Severity</th>
      <th>Count</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="badge-high">High</span></td>
      <td>{cross_counts["HIGH"]}</td>
      <td>Cross-dataset inconsistencies that may materially affect confidence in employee lifecycle, payroll sequencing, or linked record integrity.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>{cross_counts["MEDIUM"]}</td>
      <td>Cross-module mismatches or data linkage issues that warrant review but may be explainable through timing, process, or source-system differences.</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>{cross_counts["LOW"]}</td>
      <td>Lower-impact cross-module inconsistencies that should be monitored and improved over time.</td>
    </tr>
  </tbody>
</table>

---
""".strip()


# ======================================
# Limitations / Next Steps / Appendices
# ======================================

def build_limitations() -> str:
    return """This review is subject to the following limitations:

- Calculations assume the underlying pay rates, loadings and multipliers are correct in the source systems.
- Award and enterprise agreement interpretation is not performed by this tool.
- Holiday calendars, leave rules and accrual settings are assumed to reflect the organisation’s intended configuration.
- Data quality issues (missing records, duplicates, inconsistent identifiers) may affect the completeness and accuracy of the results.

---
""".strip()


def build_next_steps(base_output_dir: Path | None = None) -> str:
    return """1. Validate the highest-severity findings first.
2. Review the most affected modules and confirm whether findings reflect genuine control issues or data limitations.
3. Address structural data gaps that weaken evidentiary confidence.
4. Confirm root causes before remediation.
5. Re-run the review after corrective action to confirm that risk indicators have reduced.

---
""".strip()


def build_appendices(
    included_modules: set[str] | list[str] | None = None,
    base_output_dir: Path | None = None,
) -> str:
    mods = {m.strip().upper() for m in (included_modules or set())}
    lines: List[str] = []

    lines.append("### Appendix A – Rule Definitions")
    lines.append("")
    lines.append("This review used a set of automated rules to flag evidential and process risk indicators.")
    lines.append("")

    if "LEAVE" in mods:
        lines.append("#### Leave & Entitlement Leakage")
        lines.append("")
        lines.append("- Negative balance checks")
        lines.append("- Casual employees accruing leave")
        lines.append("- Inactive or terminated employees with leave movements")
        lines.append("- Unusual accrual or usage patterns")
        lines.append("")

    if "LSL" in mods:
        lines.append("#### Long Service Leave (LSL) Exposure")
        lines.append("")
        lines.append("- Inconsistent LSL accrual patterns")
        lines.append("- LSL balances inconsistent with service duration")
        lines.append("- Missing or incomplete service date records")
        lines.append("")

    if "TERM" in mods:
        lines.append("#### Termination Exposure (TERM)")
        lines.append("")
        lines.append("- Final pay sequencing checks vs termination date")
        lines.append("- Missing / inconsistent termination dates")
        lines.append("- Missing / inconsistent termination type / reason")
        lines.append("- Missing evidence references / artefact identifiers")
        lines.append("- Ambiguous identification of final pay events within a window")
        lines.append("- Termination events inconsistent with ordinary pay activity patterns")
        lines.append("")

    if "RKEG" in mods:
        lines.append("#### Record-Keeping & Evidence Gaps (RKEG)")
        lines.append("")
        lines.append("- Missing employee master data fields")
        lines.append("- Orphan pay events and traceability gaps")
        lines.append("- Inconsistent employment status records")
        lines.append("- Missing or inconsistent termination attributes")
        lines.append("")

    if "CROSS_MODULE" in mods:
        lines.append("#### Cross-Module Integrity (CROSS_MODULE)")
        lines.append("")
        lines.append("- Employee lifecycle mismatches across datasets")
        lines.append("- Leave activity inconsistent with employment or termination status")
        lines.append("- Payroll events inconsistent with linked employee or termination records")
        lines.append("- Cross-dataset linkage or sequencing anomalies")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("### Appendix B – Machine-readable outputs")
    lines.append("")
    lines.append(
        "Complete machine-readable outputs are available in the generated CSV and summary files for the modules included in this engagement."
    )
    lines.append("")
    lines.append(
        "These files provide row-level detail suitable for operational review, sampling, remediation planning, or incorporation into a broader audit work program."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)