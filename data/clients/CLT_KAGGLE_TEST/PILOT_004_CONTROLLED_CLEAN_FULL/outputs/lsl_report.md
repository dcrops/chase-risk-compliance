<div class="cover-page">
  <div class="cover-brand">
    <img src="file:///C:/Users/dcropper/Projects/chase-risk-compliance/src/reporting/assets/crc_logo_full.png" alt="Chase Risk & Compliance" class="cover-logo">
  </div>

  <div class="cover-kicker">Payroll Risk &amp; Evidence Review</div>
  <div class="cover-title">Long Service Leave (LSL) Exposure Review</div>

  <div class="cover-meta-card">
    <div class="cover-meta-row">
      <span class="cover-meta-label">Organisation</span>
      <span class="cover-meta-value">Chase Risk &amp; Compliance Demo Client</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Review period</span>
      <span class="cover-meta-value">15 Feb 2010 to 10 Apr 2024</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Prepared as at</span>
      <span class="cover-meta-value">10 Apr 2026</span>
    </div>
  </div>

  <div class="cover-confidentiality">Confidential</div>
</div>
<h2 class="page-break-before">1. Executive Summary</h2>

This Long Service Leave (LSL) report focuses solely on LSL-related risk indicators identified from the supplied payroll and HR data. A total of 0 potential issues were identified across approximately 0 employees. These findings range from likely LSL under- or over-provisioning risk through to data and configuration issues that may affect the reliability of reported LSL liabilities.

Across the dataset provided, the automated checks identified:

- **High:** 0
- **Medium:** 0
- **Low:** 0

A detailed breakdown by severity is provided in the **Findings Overview** section.

<h2 class="page-break-before">2. Data Sources</h2>

This review was generated from the following analysis outputs within the project `outputs/` directory:

- `lsl_summary_by_severity.csv`  
- `lsl_findings.csv`  
- `executive\executive_summary.md`  
- `executive\executive_summary.json`  
- `crc_coverage_insight.md`  

These outputs were produced by rule-based checks over payroll and HR CSV extracts supplied by the organisation for the review period.

---

<h2 class="page-break-before">3. Scope & Methodology</h2>

**Modules included in this engagement:**

- Long Service Leave Exposure (LSL)

---

### **Long Service Leave (LSL) Exposure – Scope & Methodology**

**Scope**

The Long Service Leave (LSL) Exposure review identifies risk indicators in LSL balance and service-related data that may warrant further validation. The purpose of this review is to highlight records that appear inconsistent, incomplete, or difficult to substantiate based on the data provided.

This review is designed to support payroll, HR and finance teams in prioritising follow-up effort. Findings are risk signals only and do not, on their own, confirm an entitlement error, underpayment, or non-compliance.

**Data reviewed**

- employee master data relevant to LSL service (where supplied)
- LSL balance snapshot data (where supplied)
- LSL accrual or movement records (where supplied)
- other supporting payroll extracts included in the engagement pack

**Checks performed**

- consistency checks between LSL balances, accrual patterns, and available service-related fields
- identification of missing or incomplete service date records required to support LSL calculations
- detection of unusual balance or movement patterns that may indicate configuration or data issues

**Out of scope**

This review does not:

- interpret awards, enterprise agreements, or employment contracts
- calculate legal LSL entitlement outcomes or confirm the correctness of LSL accrual rules
- provide legal, accounting, or industrial relations advice
- assert contraventions of legislation or confirm non-compliance.

Where any exposure estimates or balance concerns are inferred, they are indicative only and must be validated before remediation or accounting decisions are made.

---

<h2>4. Findings Overview</h2>

<h2>5. Detailed Findings</h2>

<div class="no-findings">
No LSL-related findings were identified for the supplied data.
</div>

<h2>6. Financial Exposure (Indicative)</h2>

No LSL exposure estimates were available from the current data extract. If required, aggregated LSL exposure figures can be added to this section in future runs.

---

<h2>7. Limitations & Assumptions</h2>

This review is subject to the following limitations:

- Calculations assume the underlying pay rates, loadings and multipliers are correct in the source systems.
- Award and enterprise agreement interpretation is not performed by this tool.
- Holiday calendars, leave rules and accrual settings are assumed to reflect the organisation’s intended configuration.
- Data quality issues (missing records, duplicates, inconsistent identifiers) may affect the completeness and accuracy of the results.

---

<h2>8. Recommended Next Steps</h2>

1. Validate the highest-severity findings first.
2. Review the most affected modules and confirm whether findings reflect genuine control issues or data limitations.
3. Address structural data gaps that weaken evidentiary confidence.
4. Confirm root causes before remediation.
5. Re-run the review after corrective action to confirm that risk indicators have reduced.

---

<h2 class="page-break-before">9. Appendices</h2>

### Appendix A – Rule Definitions

This review used a set of automated rules to flag evidential and process risk indicators.

#### Long Service Leave (LSL) Exposure

- Inconsistent LSL accrual patterns
- LSL balances inconsistent with service duration
- Missing or incomplete service date records

---

### Appendix B – Machine-readable outputs

Complete machine-readable outputs are available in the generated CSV and summary files for the modules included in this engagement.

These files provide row-level detail suitable for operational review, sampling, remediation planning, or incorporation into a broader audit work program.

---
