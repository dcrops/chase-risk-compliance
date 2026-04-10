<div class="cover-page">
  <div class="cover-brand">
    <img src="file:///C:/Users/dcropper/Projects/chase-risk-compliance/src/reporting/assets/crc_logo_full.png" alt="Chase Risk & Compliance" class="cover-logo">
  </div>

  <div class="cover-kicker">Payroll Risk &amp; Evidence Review</div>
  <div class="cover-title">Record-Keeping &amp; Evidence Gaps (RKEG)</div>

  <div class="cover-meta-card">
    <div class="cover-meta-row">
      <span class="cover-meta-label">Organisation</span>
      <span class="cover-meta-value">Organisation name not provided</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Review period</span>
      <span class="cover-meta-value">01 Mar 2024 to 20 Apr 2024</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Prepared as at</span>
      <span class="cover-meta-value">10 Apr 2026</span>
    </div>
  </div>

  <div class="cover-confidentiality">Confidential</div>
</div>
<h2 class="page-break-before">1. Executive Summary</h2>

This Record-Keeping & Evidence Gaps (RKEG) report focuses solely on evidential risk indicators identified from the supplied payroll and HR data. The review assesses how complete, consistent and traceable payroll-related records appear for audit and dispute purposes. It does **not** determine whether payroll outcomes are correct or incorrect under applicable legislation, awards or agreements.

Across the dataset provided, the automated checks identified:

- **High:** 3
- **Medium:** 1
- **Low:** 0

A detailed breakdown by severity is provided in the **Findings Overview** section.

<h2 class="page-break-before">2. Data Sources</h2>

This review was generated from the following analysis outputs within the project `outputs/` directory:

- `rkeg_summary_by_severity.csv`  
- `rkeg_findings.csv`  
- `executive\executive_summary.md`  
- `executive\executive_summary.json`  

These outputs were produced by rule-based checks over payroll and HR CSV extracts supplied by the organisation for the review period.

---

<h2 class="page-break-before">3. Scope & Methodology</h2>

**Modules included in this engagement:**

- Record-Keeping & Evidence Gaps (RKEG)

---

### **Record-Keeping & Evidence Gaps (RKEG) – Scope & Methodology**

**Scope**

The Record-Keeping & Evidence Gaps (RKEG) review assesses whether payroll-related records are sufficiently complete, consistent and traceable to support the organisation’s ability to evidence payroll decisions if reviewed by auditors or regulators.

RKEG focuses on evidential strength, not on determining whether payroll outcomes are correct or incorrect. Findings highlight where records may be incomplete, inconsistent, or difficult to substantiate if challenged.

This review is intended to support risk-aware payroll operations by identifying evidence weaknesses that can increase audit effort, increase dispute risk, or reduce the organisation’s ability to confidently explain pay decisions.

**Data reviewed**

- employee master data (where supplied)
- pay event / payroll transaction extracts (where supplied)
- termination and employment status fields where included in the engagement data pack

**Checks performed**

- completeness checks for key employee master fields required for traceability and defensibility
- identification of orphan or untraceable pay events (for example, pay events with missing or inconsistent identifiers)
- consistency checks across employee status and payroll activity where possible
- identification of gaps that may require manual reconstruction to support an audit trail

**Out of scope**

This review does not:

- calculate entitlements, underpayments or overpayments
- interpret awards, enterprise agreements, or employment contracts
- provide legal, accounting, or industrial relations advice
- assert contraventions of legislation or confirm non-compliance.

RKEG findings should be interpreted as evidential risk indicators. Addressing them improves defensibility and reduces audit effort, but does not necessarily imply a payroll outcome is incorrect.

---

<h2>4. Findings Overview</h2>

As part of this review, a Record-Keeping & Evidence Gaps (RKEG) assessment was performed to evaluate whether payroll-related records are sufficiently complete, consistent and traceable to support payroll decisions if subject to audit or regulatory review.

The RKEG assessment focuses on evidential strength only. It does not determine whether payroll outcomes are correct or incorrect, and does not interpret awards, enterprise agreements or employment contracts.

The table below summarises the number of record-keeping and evidence gaps identified by severity. Counts reflect **evidential risk** only and do not represent confirmed non-compliance or quantified financial exposure.

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
      <td>3</td>
      <td>Absence or weakness of core evidence or entitlement configuration that would materially impair the organisation’s ability to evidence payroll decisions if reviewed by auditors or regulators.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>1</td>
      <td>Evidence is incomplete, inconsistent or fragile. Decisions may still be defensible but require greater reliance on manual reconstruction, judgement, or explanation.</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>0</td>
      <td>Record-keeping or data quality weaknesses that are unlikely to be challenged in isolation but should be improved over time to support efficient and reliable payroll operations.</td>
    </tr>
  </tbody>
</table>

---

<h2>5. Detailed Findings</h2>

This section sets out detailed findings for <strong>Record-Keeping &amp; Evidence Gaps (RKEG)</strong> only.
Findings highlight where payroll-related records may be incomplete, inconsistent or difficult
to substantiate if reviewed by auditors, regulators or in the context of a dispute.
They do <strong>not</strong> confirm incorrect pay outcomes.

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">RKEG-PAY-010</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | As at: 2024-04-20 | Classification: LOGICAL</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Pay events were identified that fall outside the employee&#x27;s recorded employment period.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may increase evidential and audit risk in relation to payroll records. Weak, incomplete or inconsistent records can reduce the organisation&#x27;s ability to respond confidently if challenged.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Reconcile pay events against employment start and termination dates and investigate any payments recorded outside valid employment periods.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;pay_events.csv&quot;, &quot;employees.csv&quot;, &quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;}, &quot;values&quot;: {&quot;pay_date&quot;: &quot;2024-04-20&quot;, &quot;start_date&quot;: &quot;2018-06-01&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;days_after_termination&quot;: 50}, &quot;thresholds&quot;: {&quot;allowed_days_after_term&quot;: 14, &quot;high_severity_cutoff_days&quot;: 30}, &quot;explanation&quot;: &quot;Pay event occurred significantly after the recorded termination date, indicating a likely inconsistency between employment period and payroll activity.&quot;}</pre>
</div>
</div>

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">RKEG-TERM-001</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | As at: 2024-03-01 | Classification: LOGICAL</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">One or more terminated employees appear to have received final pay outside the configured statutory timeframe.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may increase evidential and audit risk in relation to payroll records. Weak, incomplete or inconsistent records can reduce the organisation&#x27;s ability to respond confidently if challenged.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review termination processing workflows and ensure final pay is calculated and processed within the required statutory timeframe.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;derived_final_pay_date&quot;: &quot;2024-04-20&quot;, &quot;days_after_termination&quot;: 50}, &quot;thresholds&quot;: {&quot;max_days_after_termination&quot;: 7}, &quot;explanation&quot;: &quot;Latest pay event on or after termination date exceeds the configured final pay timing threshold.&quot;}</pre>
</div>
</div>

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">RKEG-TERM-001</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | As at: 2024-03-01 | Classification: LOGICAL</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">One or more terminated employees appear to have received final pay outside the configured statutory timeframe.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may increase evidential and audit risk in relation to payroll records. Weak, incomplete or inconsistent records can reduce the organisation&#x27;s ability to respond confidently if challenged.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review termination processing workflows and ensure final pay is calculated and processed within the required statutory timeframe.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;derived_final_pay_date&quot;: &quot;2024-03-10&quot;, &quot;days_after_termination&quot;: 9}, &quot;thresholds&quot;: {&quot;max_days_after_termination&quot;: 7}, &quot;explanation&quot;: &quot;Latest pay event on or after termination date exceeds the configured final pay timing threshold.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">RKEG-GOV-001</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Classification: STRUCTURAL</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">No structured override or exception log was provided for manual payroll adjustments.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may increase evidential and audit risk in relation to payroll records. Weak, incomplete or inconsistent records can reduce the organisation&#x27;s ability to respond confidently if challenged.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Introduce a basic override register or system-based workflow to record all manual payroll changes, including who made the change, when, and for what reason.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;pay_overrides.csv&quot;], &quot;primary_keys&quot;: {}, &quot;values&quot;: {}, &quot;explanation&quot;: &quot;No structured pay_overrides dataset was provided, or the dataset was empty.&quot;}</pre>
</div>
</div>

<h2>6. Limitations & Assumptions</h2>

This review is subject to the following limitations:

- Calculations assume the underlying pay rates, loadings and multipliers are correct in the source systems.
- Award and enterprise agreement interpretation is not performed by this tool.
- Holiday calendars, leave rules and accrual settings are assumed to reflect the organisation’s intended configuration.
- Data quality issues (missing records, duplicates, inconsistent identifiers) may affect the completeness and accuracy of the results.

---

<h2>7. Recommended Next Steps</h2>

1. Validate the highest-severity findings first.
2. Review the most affected modules and confirm whether findings reflect genuine control issues or data limitations.
3. Address structural data gaps that weaken evidentiary confidence.
4. Confirm root causes before remediation.
5. Re-run the review after corrective action to confirm that risk indicators have reduced.

---

<h2 class="page-break-before">8. Appendices</h2>

### Appendix A – Rule Definitions

This review used a set of automated rules to flag evidential and process risk indicators.

#### Record-Keeping & Evidence Gaps (RKEG)

- Missing employee master data fields
- Orphan pay events and traceability gaps
- Inconsistent employment status records
- Missing or inconsistent termination attributes

---

### Appendix B – Machine-readable outputs

Complete machine-readable outputs are available in the generated CSV and summary files for the modules included in this engagement.

These files provide row-level detail suitable for operational review, sampling, remediation planning, or incorporation into a broader audit work program.

---
