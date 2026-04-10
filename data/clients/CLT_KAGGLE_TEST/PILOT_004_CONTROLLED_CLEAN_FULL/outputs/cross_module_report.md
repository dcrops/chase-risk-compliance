<div class="cover-page">
  <div class="cover-brand">
    <img src="file:///C:/Users/dcropper/Projects/chase-risk-compliance/src/reporting/assets/crc_logo_full.png" alt="Chase Risk & Compliance" class="cover-logo">
  </div>

  <div class="cover-kicker">Payroll Risk &amp; Evidence Review</div>
  <div class="cover-title">Cross-Module Integrity</div>

  <div class="cover-meta-card">
    <div class="cover-meta-row">
      <span class="cover-meta-label">Organisation</span>
      <span class="cover-meta-value">Chase Risk &amp; Compliance Demo Client</span>
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

This Cross-Module Integrity report focuses solely on inconsistencies identified between related payroll datasets, including employee lifecycle, leave activity, payroll events, and termination-related records.

A total of 12 cross-module integrity findings were identified across approximately 2 employees. These findings indicate possible linkage, sequencing, lifecycle, or dataset alignment weaknesses that may reduce confidence in the broader payroll data environment.

Across the dataset provided, the automated checks identified:

- **High:** 5
- **Medium:** 7
- **Low:** 0

A detailed breakdown by severity is provided in the **Findings Overview** section.

<h2 class="page-break-before">2. Data Sources</h2>

This review was generated from the following analysis outputs within the project `outputs/` directory:

- `cross_module_summary_by_severity.csv`  
- `cross_module_findings.csv`  
- `executive\executive_summary.md`  
- `executive\executive_summary.json`  
- `crc_coverage_insight.md`  

These outputs were produced by rule-based checks over payroll and HR CSV extracts supplied by the organisation for the review period.

---

<h2 class="page-break-before">3. Scope & Methodology</h2>

**Modules included in this engagement:**

- Cross-Module Integrity (CROSS_MODULE)

---

### **Cross-Module Integrity – Scope & Methodology**

**Scope**

The Cross-Module Integrity review assesses whether related payroll datasets align consistently across employee lifecycle, leave, payroll event, and termination records.

The purpose of this review is to identify inconsistencies between linked datasets that may indicate sequencing issues, lifecycle mismatches, incomplete integrations, or broader payroll data integrity weaknesses.

This review is designed to support payroll, HR, finance, and governance teams in identifying where records may not align cleanly across the broader payroll data environment. Findings are integrity signals only and do not, on their own, confirm non-compliance, underpayment, or payroll error.

**Data reviewed**

- employee master data (where supplied)
- leave balances and leave movement data (where supplied)
- payroll event / payroll transaction extracts (where supplied)
- termination and lifecycle-related records where included in the engagement data pack

**Checks performed**

- consistency checks between employee lifecycle status and payroll activity
- identification of mismatches between leave activity and termination or employment status
- cross-dataset linkage checks for related employee and payroll records
- detection of sequencing anomalies between linked events across modules

**Out of scope**

This review does not:

- calculate entitlements, underpayments or overpayments
- interpret awards, enterprise agreements, or employment contracts
- provide legal, accounting, or industrial relations advice
- assert contraventions of legislation or confirm non-compliance.

Cross-module findings should be interpreted as data integrity and linkage risk indicators. They highlight where records may not align cleanly across datasets and may require investigation before conclusions are drawn.

---

<h2>4. Findings Overview</h2>

Where a Cross-Module Integrity review was performed, the table below summarises the number of cross-module inconsistencies identified by severity. Counts reflect **integrity risk indicators only** and do not represent confirmed non-compliance or quantified financial exposure.

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
      <td>5</td>
      <td>Cross-dataset inconsistencies that may materially affect confidence in employee lifecycle, payroll sequencing, or linked record integrity.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>7</td>
      <td>Cross-module mismatches or data linkage issues that warrant review but may be explainable through timing, process, or source-system differences.</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>0</td>
      <td>Lower-impact cross-module inconsistencies that should be monitored and improved over time.</td>
    </tr>
  </tbody>
</table>

---

<h2>5. Detailed Findings</h2>

This section sets out detailed findings for <strong>Cross-Module Integrity</strong> only.
Findings highlight potential sequencing, lifecycle, and dataset-alignment issues across related payroll records.
They are integrity indicators and do <strong>not</strong> on their own confirm non-compliance or incorrect pay outcomes.

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-003</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-04-20</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">A termination record has no supporting evidence reference and payroll activity continues after the termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review termination evidence records and confirm whether payroll activity after termination was valid or requires correction.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">51bf850dc85e</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;pay_date&quot;: &quot;2024-04-20&quot;}, &quot;values&quot;: {&quot;evidence_reference&quot;: null, &quot;days_after_termination&quot;: 50, &quot;gross_amount&quot;: 2500.0}, &quot;thresholds&quot;: {&quot;allowed_days_after_term&quot;: 14, &quot;high_severity_cutoff_days&quot;: 30}, &quot;explanation&quot;: &quot;Termination evidence reference is missing and payroll activity continues significantly after termination, indicating a likely lifecycle control breakdown.&quot;}</pre>
</div>
</div>

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-006</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: LOGICAL | Dates: 2024-03-01 → 2024-04-10</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Payroll activity and leave ledger movement both continue after the employee termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review the employee termination timeline, payroll activity, and leave transactions to confirm whether the employee was correctly finalised.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">1ba6ace90e24</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;pay_events.csv&quot;, &quot;leave_ledger.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;has_post_term_payroll_activity&quot;: true, &quot;has_post_term_leave_activity&quot;: true, &quot;latest_post_term_leave_date&quot;: &quot;2024-04-10&quot;, &quot;max_days_after_termination_pay&quot;: 50}, &quot;thresholds&quot;: {&quot;allowed_days_after_term&quot;: 14, &quot;high_severity_cutoff_days&quot;: 30}, &quot;explanation&quot;: &quot;Payroll activity and leave ledger movement both continue significantly after termination, indicating a likely breakdown in off-boarding control integrity.&quot;}</pre>
</div>
</div>

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-017</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: LOGICAL | Event: 2024-03-05</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">A final pay event was flagged but no termination evidence reference exists.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Ensure termination evidence such as resignation or termination documentation is recorded and linked to payroll records.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">061dc6f73892</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;issue&quot;: &quot;final pay without evidence&quot;, &quot;evidence_reference&quot;: null}</pre>
</div>
</div>

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-017</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Classification: LOGICAL | Event: 2024-03-10</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">A final pay event was flagged but no termination evidence reference exists.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Ensure termination evidence such as resignation or termination documentation is recorded and linked to payroll records.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">061dc6f73892</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;issue&quot;: &quot;final pay without evidence&quot;, &quot;evidence_reference&quot;: null}</pre>
</div>
</div>

<div class="finding high">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-020</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-high">HIGH</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: CONTEXTUAL</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">An employee triggered multiple cross-module integrity failures.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review the full lifecycle of the employee including payroll, leave, termination and evidence records.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">050e64ad6d2a</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;total_findings&quot;: 6, &quot;high_findings&quot;: 3, &quot;thresholds&quot;: {&quot;min_findings&quot;: 3, &quot;min_high_severity&quot;: 2}, &quot;explanation&quot;: &quot;The employee triggered multiple cross-module integrity failures, including multiple high-severity signals, indicating a likely systemic lifecycle control breakdown.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-002</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Related record / leave type: ANNUAL | Classification: CONTEXTUAL | Dates: 2024-03-01 → 2024-04-10</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Leave ledger movement was recorded after the employee termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review termination timing and leave processing history to confirm whether the movement is valid and properly evidenced.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">0b7e46d4abc1</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;leave_ledger.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;event_date&quot;: &quot;2024-04-10&quot;, &quot;leave_type&quot;: &quot;ANNUAL&quot;}, &quot;values&quot;: {&quot;event_type&quot;: null, &quot;units&quot;: 8.0}, &quot;explanation&quot;: &quot;Leave ledger movement was recorded after the employee termination date.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-002</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Related record / leave type: ANNUAL | Classification: CONTEXTUAL | Dates: 2024-03-01 → 2024-03-15</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Leave ledger movement was recorded after the employee termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review termination timing and leave processing history to confirm whether the movement is valid and properly evidenced.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">3f3de4c61b56</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;leave_ledger.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;event_date&quot;: &quot;2024-03-15&quot;, &quot;leave_type&quot;: &quot;ANNUAL&quot;}, &quot;values&quot;: {&quot;event_type&quot;: null, &quot;units&quot;: 4.0}, &quot;explanation&quot;: &quot;Leave ledger movement was recorded after the employee termination date.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-012</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Related record / leave type: ANNUAL | Classification: CONTEXTUAL | Dates: 2024-03-01 → 2024-04-10</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Leave ledger activity was recorded after the employee termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Confirm whether the employee was reinstated or whether the ledger events were posted incorrectly.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">ca37a32075d0</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;leave_ledger.csv&quot;, &quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;event_date&quot;: &quot;2024-04-10&quot;, &quot;leave_type&quot;: &quot;ANNUAL&quot;}, &quot;values&quot;: {&quot;event_type&quot;: &quot;nan&quot;, &quot;units&quot;: 8.0, &quot;days_after_termination&quot;: 40}, &quot;thresholds&quot;: {&quot;allowed_event_types&quot;: [&quot;ADJUSTMENT&quot;, &quot;PAYOUT&quot;]}, &quot;explanation&quot;: &quot;Leave ledger activity was recorded after the employee termination date.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-012</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Related record / leave type: ANNUAL | Classification: CONTEXTUAL | Dates: 2024-03-01 → 2024-03-15</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">Leave ledger activity was recorded after the employee termination date.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Confirm whether the employee was reinstated or whether the ledger events were posted incorrectly.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">d73511e58fab</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;leave_ledger.csv&quot;, &quot;terminations.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;, &quot;event_date&quot;: &quot;2024-03-15&quot;, &quot;leave_type&quot;: &quot;ANNUAL&quot;}, &quot;values&quot;: {&quot;event_type&quot;: &quot;nan&quot;, &quot;units&quot;: 4.0, &quot;days_after_termination&quot;: 14}, &quot;thresholds&quot;: {&quot;allowed_event_types&quot;: [&quot;ADJUSTMENT&quot;, &quot;PAYOUT&quot;]}, &quot;explanation&quot;: &quot;Leave ledger activity was recorded after the employee termination date.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-016</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E002 | Classification: STRUCTURAL | Termination: 2024-03-01</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">A termination record exists but no supporting leave snapshot record was identified for the employee.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review snapshot extract completeness and confirm whether terminated employees were intentionally excluded or whether leave balances were missing from the extract.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">ca93e3ef4ed9</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;balances_snapshot.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E002&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;leave_snapshot_record_found&quot;: false}, &quot;thresholds&quot;: {&quot;leave_types_checked&quot;: [&quot;ANNUAL&quot;, &quot;LSL&quot;]}, &quot;explanation&quot;: &quot;A termination record exists but no supporting leave snapshot record was identified for the employee.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-016</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Classification: STRUCTURAL | Termination: 2024-03-01</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">A termination record exists but no supporting leave snapshot record was identified for the employee.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review snapshot extract completeness and confirm whether terminated employees were intentionally excluded or whether leave balances were missing from the extract.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">81c9d3c56fec</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;sources&quot;: [&quot;terminations.csv&quot;, &quot;balances_snapshot.csv&quot;], &quot;primary_keys&quot;: {&quot;employee_id&quot;: &quot;E005&quot;, &quot;termination_date&quot;: &quot;2024-03-01&quot;}, &quot;values&quot;: {&quot;leave_snapshot_record_found&quot;: false}, &quot;thresholds&quot;: {&quot;leave_types_checked&quot;: [&quot;ANNUAL&quot;, &quot;LSL&quot;]}, &quot;explanation&quot;: &quot;A termination record exists but no supporting leave snapshot record was identified for the employee.&quot;}</pre>
</div>
</div>

<div class="finding medium">
  <div class="finding-header">
    <div class="finding-title-wrap">
      <div class="finding-title">CM-020</div>
    </div>
    <div class="finding-badge-wrap">
      <span class="badge-medium">MEDIUM</span>
    </div>
  </div>

  <div class="finding-meta">Employee: E005 | Classification: CONTEXTUAL</div>

  <div class="finding-section">
  <div class="finding-label">Finding</div>
  <div class="finding-text finding-main">An employee triggered multiple cross-module integrity failures.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Impact</div>
  <div class="finding-text finding-impact">This may indicate data integrity, sequencing, or lifecycle mismatches across related payroll datasets. These issues can reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Recommendation</div>
  <div class="finding-text finding-action">Review the full lifecycle of the employee including payroll, leave, termination and evidence records.</div>
</div>
  <div class="finding-section">
  <div class="finding-label">Finding ID</div>
  <div class="finding-text">050e64ad6d2a</div>
</div>
  
<div class="finding-section">
  <div class="finding-label">Evidence Reference</div>
  <pre class="finding-evidence">{&quot;total_findings&quot;: 4, &quot;high_findings&quot;: 1, &quot;thresholds&quot;: {&quot;min_findings&quot;: 3, &quot;min_high_severity&quot;: 2}, &quot;explanation&quot;: &quot;The employee triggered multiple cross-module integrity failures, indicating a clustered lifecycle control issue that should be reviewed in context.&quot;}</pre>
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

#### Cross-Module Integrity (CROSS_MODULE)

- Employee lifecycle mismatches across datasets
- Leave activity inconsistent with employment or termination status
- Payroll events inconsistent with linked employee or termination records
- Cross-dataset linkage or sequencing anomalies

---

### Appendix B – Machine-readable outputs

Complete machine-readable outputs are available in the generated CSV and summary files for the modules included in this engagement.

These files provide row-level detail suitable for operational review, sampling, remediation planning, or incorporation into a broader audit work program.

---
