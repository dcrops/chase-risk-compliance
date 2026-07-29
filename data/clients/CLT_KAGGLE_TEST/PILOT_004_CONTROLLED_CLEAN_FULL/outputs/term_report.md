<div class="cover-page">
  <div class="cover-brand">
    <img src="file:///C:/Users/dcropper/Projects/chase-risk-compliance/src/reporting/assets/crc_logo_full.png" alt="Chase Risk & Compliance" class="cover-logo">
  </div>

  <div class="cover-kicker">Payroll Risk &amp; Evidence Review</div>
  <div class="cover-title">Termination Exposure – Detailed Report</div>

  <div class="cover-meta-card">
    <div class="cover-meta-row">
      <span class="cover-meta-label">Organisation</span>
      <span class="cover-meta-value">Organisation name not provided</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Review period</span>
      <span class="cover-meta-value">01 Mar 2024</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Prepared as at</span>
      <span class="cover-meta-value">09 Jul 2026</span>
    </div>
  </div>

  <div class="cover-confidentiality">Confidential</div>
</div>
<h2 class="page-break-before">1. Executive Summary</h2>

This Termination Exposure report focuses solely on termination-related evidential risk indicators identified from the supplied payroll and HR data. The review assesses how complete, timely and traceable termination records appear for audit and dispute purposes. It does **not** determine whether termination payments are correct under applicable awards, agreements or contracts.

Across the dataset provided, the automated checks identified:

- **High:** 2
- **Medium:** 8
- **Low:** 0

A detailed breakdown by severity is provided in the **Findings Overview** section.

<h2 class="page-break-before">2. Data Sources</h2>

This review was generated from the following analysis outputs within the project `outputs/` directory:

- `term_summary_by_severity.csv`  
- `term_findings.csv`  
- `executive\executive_summary.md`  
- `executive\executive_summary.json`  
- `crc_coverage_insight.md`  

These outputs were produced by rule-based checks over payroll and HR CSV extracts supplied by the organisation for the review period.

---

<h2 class="page-break-before">3. Scope & Methodology</h2>

**Modules included in this engagement:**

- Termination Exposure (TERM)

---

### **Termination Exposure – Scope & Methodology**

**Scope**

The Termination Exposure review assesses whether termination events recorded in payroll and related employment data are sufficiently complete, timely, and traceable to support the organisation’s ability to evidence termination-related payroll decisions if reviewed by auditors or regulators.

This review focuses on process and evidential integrity, not on the correctness of termination payments.

Specifically, the review considers whether:

- termination events are recorded consistently across available data sources
- final pay processing occurs in a reasonable and defensible sequence relative to termination dates
- core termination attributes (such as termination date and termination type/reason) are present and internally consistent
- termination-related decisions are supported by basic evidentiary artefacts or references

**Out of scope**

This review does not:

- calculate final pay entitlements or assess payment correctness
- interpret awards, enterprise agreements, or employment contracts
- determine notice, redundancy, or severance obligations
- assert contraventions of legislation or confirm non-compliance.
- provide legal advice or assurance of compliance.

Any potential exposure identified reflects defensibility risk, not confirmed error or liability.

**Methodology**

The review applies a series of rule-based checks to payroll and related employment data to identify termination events that exhibit characteristics commonly associated with audit, regulatory, or dispute risk.

Each finding is assigned a severity based on evidential impact, reflecting how materially the issue could impair the organisation’s ability to explain and support termination-related payroll decisions if reviewed.

Severity does not represent:

- likelihood of underpayment
- magnitude of potential monetary impact
- remediation priority

---

<h2>4. Findings Overview</h2>

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
      <td>2</td>
      <td>Absence or weakness of core termination or final pay evidence that would materially impair the organisation’s ability to evidence termination decisions if reviewed by auditors or regulators.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>8</td>
      <td>Termination evidence exists but is incomplete, delayed or ambiguous and may require additional explanation or manual reconstruction.</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>0</td>
      <td>Minor record-keeping or data quality weaknesses in termination records that should be improved over time to support efficient and reliable payroll operations.</td>
    </tr>
  </tbody>
</table>

---

<h2>5. Detailed Findings</h2>

This section sets out detailed findings for **Termination Exposure** only. Findings highlight where termination records may be incomplete, inconsistent or difficult to substantiate if reviewed by auditors, regulators or in the context of a dispute. They do **not** confirm incorrect pay outcomes.

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-010</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-04-20</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Payroll activity was recorded after the employee termination date beyond the allowed tolerance window.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review the termination date and subsequent payroll activity to confirm whether the employee was correctly finalised.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;pay_date&quot;: &quot;2024-04-20&quot;}, &quot;values&quot;: {&quot;gross_amount&quot;: 2500.0, &quot;is_final_pay&quot;: &quot;False&quot;, &quot;days_after_termination&quot;: 50}, &quot;thresholds&quot;: {&quot;allowed_days_after_term&quot;: 14, &quot;high_severity_cutoff_days&quot;: 30}, &quot;explanation&quot;: &quot;Payroll activity continued significantly after termination, indicating a likely inconsistency between lifecycle status and payroll activity.&quot;}</pre>
</div>
</div>

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-015</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-04-20</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Multiple payroll events were recorded after the termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Confirm whether the employee continued employment or whether payroll processing was incorrect.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;post_term_pay_count&quot;: 2, &quot;first_post_term_pay_date&quot;: &quot;2024-03-05&quot;, &quot;last_post_term_pay_date&quot;: &quot;2024-04-20&quot;}, &quot;explanation&quot;: &quot;Multiple payroll events were recorded after the employee termination date.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-004</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: STRUCTURAL | Termination: 2024-03-01</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Termination records were identified with missing or inconsistent termination type or reason information.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Ensure termination type and reason are captured consistently across HR and payroll data and reconcile conflicting values.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;termination_type&quot;: NaN, &quot;termination_reason&quot;: &quot;RESIGNATION&quot;, &quot;employee_master_termination_type&quot;: null}, &quot;explanation&quot;: &quot;Termination type or reason is missing, or inconsistent with employee master data.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-004</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Classification: STRUCTURAL | Termination: 2024-03-01</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Termination records were identified with missing or inconsistent termination type or reason information.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Ensure termination type and reason are captured consistently across HR and payroll data and reconcile conflicting values.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;termination_type&quot;: NaN, &quot;termination_reason&quot;: &quot;RESIGNATION&quot;, &quot;employee_master_termination_type&quot;: null}, &quot;explanation&quot;: &quot;Termination type or reason is missing, or inconsistent with employee master data.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-005</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: STRUCTURAL | Termination: 2024-03-01</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Termination records do not include a supporting evidence reference.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Where available, include a reference to supporting termination documentation, or confirm whether such evidence is maintained outside the payroll system.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;evidence_ref&quot;: null}, &quot;explanation&quot;: &quot;Termination record has no supporting evidence reference.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-005</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Classification: STRUCTURAL | Termination: 2024-03-01</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Termination records do not include a supporting evidence reference.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Where available, include a reference to supporting termination documentation, or confirm whether such evidence is maintained outside the payroll system.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;evidence_ref&quot;: null}, &quot;explanation&quot;: &quot;Termination record has no supporting evidence reference.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-013</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-03-05</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">A final pay event was identified without a corresponding super contribution.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review super treatment for the final pay event.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;pay_events.csv&quot;, &quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;pay_date&quot;: &quot;2024-03-05&quot;}, &quot;values&quot;: {&quot;super_amount&quot;: null, &quot;gross_amount&quot;: 2500.0, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;explanation&quot;: &quot;A final pay event was identified without a corresponding super contribution.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-013</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-03-10</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">A final pay event was identified without a corresponding super contribution.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review super treatment for the final pay event.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;pay_events.csv&quot;, &quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;pay_date&quot;: &quot;2024-03-10&quot;}, &quot;values&quot;: {&quot;super_amount&quot;: null, &quot;gross_amount&quot;: 2600.0, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;explanation&quot;: &quot;A final pay event was identified without a corresponding super contribution.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-017</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-04-20</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Payroll activity indicates the employee may have worked after the recorded termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review termination timing and payroll activity.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;last_payroll_activity_date&quot;: &quot;2024-04-20&quot;}, &quot;values&quot;: {&quot;days_after_termination&quot;: 50}, &quot;explanation&quot;: &quot;Payroll activity indicates the employee may have remained in payroll after the recorded termination date.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">TERM-017</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-03-10</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Payroll activity indicates the employee may have worked after the recorded termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may weaken the organisation&#x27;s ability to clearly evidence termination processing and final pay handling if reviewed.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review termination timing and payroll activity.</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;last_payroll_activity_date&quot;: &quot;2024-03-10&quot;}, &quot;values&quot;: {&quot;days_after_termination&quot;: 9}, &quot;explanation&quot;: &quot;Payroll activity indicates the employee may have remained in payroll after the recorded termination date.&quot;}</pre>
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

#### Termination Exposure (TERM)

- Final pay sequencing checks vs termination date
- Missing / inconsistent termination dates
- Missing / inconsistent termination type / reason
- Missing evidence references / artefact identifiers
- Ambiguous identification of final pay events within a window
- Termination events inconsistent with ordinary pay activity patterns

---

### Appendix B – Machine-readable outputs

Complete machine-readable outputs are available in the generated CSV and summary files for the modules included in this engagement.

These files provide row-level detail suitable for operational review, sampling, remediation planning, or incorporation into a broader audit work program.

---
