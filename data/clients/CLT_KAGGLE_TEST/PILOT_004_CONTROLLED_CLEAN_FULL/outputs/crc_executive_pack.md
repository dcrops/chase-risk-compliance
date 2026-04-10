<div class="cover-page">
  <div class="cover-brand">
    <img src="file:///C:/Users/dcropper/Projects/chase-risk-compliance/src/reporting/assets/crc_logo_full.png" alt="Chase Risk & Compliance" class="cover-logo">
  </div>

  <div class="cover-kicker">Payroll Risk &amp; Evidence Review</div>
  <div class="cover-title">Payroll Risk &amp; Evidence Review</div>

  <div class="cover-meta-card">
    <div class="cover-meta-row">
      <span class="cover-meta-label">Organisation</span>
      <span class="cover-meta-value">CLT Kaggle Test</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Review period</span>
      <span class="cover-meta-value">15 Feb 2010 to 20 Apr 2024</span>
    </div>
    <div class="cover-meta-row">
      <span class="cover-meta-label">Prepared as at</span>
      <span class="cover-meta-value">10 Apr 2026</span>
    </div>
  </div>

  <div class="cover-confidentiality">Confidential</div>
</div>
<h2 class="page-break-before">1. Executive Summary</h2>

- CRC identified 28 findings across the reviewed modules.
- The overall profile is primarily driven by logical integrity failures rather than structural data limitations.
- High-severity findings are concentrated in cross-module lifecycle consistency and record-keeping controls, indicating the strongest exposure sits in those areas.
- Structural findings are present, but they are not the primary driver of risk in this review.
- Findings are split between high (43%) and medium (57%) severity, indicating a mix of immediate control concerns and broader process weaknesses.

### What this means

The results suggest the main concern is substantive payroll processing and control integrity rather than simple evidentiary or data quality limitations.

### Recommended focus

Prioritise detailed review of cross-module lifecycle consistency and record-keeping controls first, then address structural data gaps that may weaken evidentiary confidence.

<h2>2. Highlight Insights</h2>

The following points summarise the most important observations from the analysis:

- The strongest concentration of risk sits in **cross-module lifecycle consistency and record-keeping controls**.
- The overall profile is dominated by **logical** findings rather than primarily structural data issues.
- Findings are split between **high (43%)** and **medium (57%) severity**, indicating a mix of immediate control concerns and broader process weaknesses.

---

<h2>3. Risk Profile Overview</h2>

This section summarises the overall risk profile across all included modules using the consolidated CRC summary outputs.

<table class="summary-table">
  <thead>
    <tr><th>Metric</th><th>Value</th></tr>
  </thead>
  <tbody>
    <tr><td>Total findings</td><td>28</td></tr>
    <tr><td>Dominant classification</td><td>LOGICAL</td></tr>
    <tr><td>Dominant severity</td><td>MEDIUM</td></tr>
    <tr><td>Logical findings</td><td>15 (54%)</td></tr>
    <tr><td>Structural findings</td><td>7 (25%)</td></tr>
    <tr><td>Contextual findings</td><td>6 (21%)</td></tr>
    <tr><td>High severity findings</td><td>12 (43%)</td></tr>
    <tr><td>Medium severity findings</td><td>16 (57%)</td></tr>
    <tr><td>Low severity findings</td><td>0 (0%)</td></tr>
  </tbody>
</table>

**Highest concentration of high-severity findings:** Cross-Module Integrity, Record-Keeping & Evidence Gaps

Classification is used to distinguish between substantive integrity issues, structural data limitations, and contextual items requiring human judgement.

---

<h2 class="page-break-before">4. Coverage & Data Dependency Insight</h2>

### What this section shows

This section compares results from two levels of analysis:

- **Payroll-only analysis** - based on core payroll datasets such as pay events, leave balances, and termination records. This provides a high-confidence baseline view of payroll integrity using readily available data.
- **Full analysis** - incorporates additional datasets (such as configuration, supporting records, or extended attributes where available), enabling broader rule coverage and deeper validation of payroll processes.

The difference between these two views reflects **coverage, not prediction**. Additional findings identified in the full analysis represent areas that are not fully assessable using payroll-only data and require broader system context to evaluate.

## Overview

- Payroll-only findings: **21**
- Full analysis findings: **28**
- Additional findings identified with broader data coverage: **7 (33%)**

**TERM** shows the largest increase in findings when additional datasets are available, with **6 additional findings** (150% increase).

## Module Breakdown

### LEAVE

- Payroll-only: 2 findings (core=2, supporting=0, extended=0)
- Full: 2 findings (core=2, supporting=0, extended=0)
- No additional findings were identified with broader datasets. This module is largely assessable using payroll-only data.

### LSL

- Payroll-only: 0 findings (core=0, supporting=0, extended=0)
- Full: 0 findings (core=0, supporting=0, extended=0)
- No additional findings were identified with broader datasets. This module is largely assessable using payroll-only data.

### TERM

- Payroll-only: 4 findings (core=4, supporting=0, extended=0)
- Full: 10 findings (core=4, supporting=0, extended=6)
- Additional findings identified: 6 (150% increase)

Termination-related risks show the strongest dependency on additional datasets. These areas are not fully assessable using payroll-only data and may only be identified when broader system context is available.

### RKEG

- Payroll-only: 3 findings (core=0, supporting=3, extended=0)
- Full: 4 findings (core=0, supporting=3, extended=1)
- Additional findings identified: 1 (33% increase)

Governance and evidence-related risks are partially observable in payroll data, with additional datasets improving both coverage and confidence of assessment.

### CROSS_MODULE

- Payroll-only: 12 findings (core=1, supporting=11, extended=0)
- Full: 12 findings (core=1, supporting=11, extended=0)
- No additional findings were identified with broader datasets. This module is fully assessable using payroll-only data and provides strong visibility into cross-dataset inconsistencies.

## Interpretation

Payroll-only analysis provides strong visibility into balance integrity, lifecycle sequencing, and cross-dataset consistency.

However, certain risk categories—particularly termination handling and governance controls—are not fully assessable without broader system context.

This reflects a coverage-based diagnostic model, where different datasets enable different levels of risk visibility.

This supports a tiered diagnostic approach:

- Payroll-only → fast, low-friction, high-confidence baseline
- Full analysis → expanded coverage and deeper risk visibility

<h2 class="page-break-before">5. Data Sources</h2>

This review was generated from the following analysis outputs within the project `outputs/` directory:

- `leave_leakage_findings.csv`  
- `leakage_report.csv`  
- `lsl_summary_by_severity.csv`  
- `lsl_findings.csv`  
- `term_summary_by_severity.csv`  
- `term_findings.csv`  
- `rkeg_summary_by_severity.csv`  
- `rkeg_findings.csv`  
- `cross_module_summary_by_severity.csv`  
- `cross_module_findings.csv`  
- `executive\executive_summary.md`  
- `executive\executive_summary.json`  
- `crc_coverage_insight.md`  

These outputs were produced by rule-based checks over payroll and HR CSV extracts supplied by the organisation for the review period.

---

<h2 class="page-break-before">6. Scope & Methodology</h2>

**Modules included in this engagement:**

- Leave & Entitlement Leakage (LEAVE)
- Long Service Leave Exposure (LSL)
- Termination Exposure (TERM)
- Record-Keeping & Evidence Gaps (RKEG)
- Cross-Module Integrity (CROSS_MODULE)

---

<h3>6.1. Leave & Entitlement Leakage – Scope & Methodology</h3>

**Scope**

The Leave & Entitlement Leakage review identifies potential anomalies and risk indicators in leave balances, accruals and leave usage based on the data provided.

The purpose of this review is to highlight records that may warrant follow-up, such as negative balances, unexpected accrual patterns, mismatches between leave activity and employee status, or inconsistencies between leave movement data and balance snapshots.

This review is designed to support payroll and HR teams in prioritising validation and remediation effort. Findings are risk signals only and do not, on their own, confirm non-compliance, underpayment, or an entitlement error.

**Data reviewed**

- leave balances snapshot data (where supplied)
- leave ledger / leave movement records (where supplied)
- employee master data (where supplied)
- other supporting payroll extracts included in the engagement pack

**Checks performed**

- rule-based detection of unusual leave balance and movement patterns
- identification of negative balances and unexpected accrual behaviour
- consistency checks between employee status and leave activity (for example, terminated employees with ongoing leave movements)
- cross-checks between leave movement data and balance snapshot fields where available

**Out of scope**

This review does not:

- interpret awards, enterprise agreements, or employment contracts
- calculate legal entitlement outcomes or confirm the correctness of leave accrual rules
- provide legal, accounting, or industrial relations advice
- assert contraventions of legislation or confirm non-compliance.

Where exposure estimates are included, they are indicative only and must be validated before remediation or accounting decisions are made.

---

<h3>6.2. Long Service Leave (LSL) Exposure – Scope & Methodology</h3>

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

<h3>6.3. Termination Exposure – Scope & Methodology</h3>

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
- magnitude of financial exposure
- remediation priority

---

<h3>6.4. Record-Keeping & Evidence Gaps (RKEG) – Scope & Methodology</h3>

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

<h3>6.5. Cross-Module Integrity – Scope & Methodology</h3>

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

<h2 class="page-break-before">7. Module Summary Overview</h2>

<h3>7.1. Leave & Entitlement Leakage (LEAVE) – Summary Overview</h3>

The automated checks identified the following potential issues in the leave and entitlement data reviewed. Severity reflects the relative level of risk to payroll accuracy and audit defensibility, not a confirmed breach.

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
      <td>Absence or weakness of core evidence or entitlement configuration that would materially impair the organisation’s ability to evidence payroll decisions if reviewed by auditors or regulators.</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>0</td>
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

<h3>7.2. Long Service Leave (LSL) – Coverage Note</h3>

<div class="no-findings">
<strong>Coverage note:</strong><br>
No Long Service Leave (LSL) activity was identified in the dataset provided for this review.

Accordingly, LSL-related diagnostics were not performed.

This reflects a data coverage limitation rather than a confirmed absence of LSL risk. Assessment of LSL exposure typically requires service history, eligibility thresholds, and accrual data that may not be present in payroll-only extracts.
</div>

---

<h3>7.3. Termination Exposure – Severity Overview</h3>

Where a Termination Exposure review was performed, the table below summarises the number of termination-related evidential issues identified by severity. Counts reflect **evidential risk only** and do not represent confirmed non-compliance or quantified financial exposure, or remediation priority.

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

<h3>7.4. Record-Keeping & Evidence Gaps (RKEG) – Severity Overview</h3>

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

<h3>7.5. Cross-Module Integrity – Summary Overview</h3>

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

<h3>7.6. How to interpret findings</h3>

**How to interpret findings across modules**

<div class="callout keep-together">
  <ul>
<li><strong>Leave &amp; LSL findings</strong> highlight potential anomalies in leave balances, accruals and usage. These indicators relate to <em>payroll outcomes and configuration</em> and may require remediation if confirmed.</li>
<li><strong>Termination Exposure findings</strong> relate to the completeness, sequencing and documentation of termination events and final pay. They indicate how readily the organisation could evidence termination processing if challenged.</li>
<li><strong>Record-Keeping &amp; Evidence Gaps (RKEG) findings</strong> assess the strength of the evidentiary trail supporting payroll decisions. They do <strong>not</strong> indicate incorrect pay outcomes; they highlight where records may be incomplete or difficult to substantiate.</li>
<li><strong>Cross-Module Integrity findings</strong> highlight inconsistencies between related datasets, such as employee lifecycle status, leave activity, and payroll events. They indicate where linked records may not align cleanly across the broader payroll data environment.</li>
</ul>

  <p>Findings are risk indicators requiring validation and do not, on their own, confirm non-compliance, legislative contravention, or underpayment.</p>
  <p><em>Severity levels reflect evidential risk and control strength, and do not represent confirmed contraventions or quantified financial exposure.</em></p>
</div>

<h2>8. Limitations & Assumptions</h2>

This review is subject to the following limitations:

- Calculations assume the underlying pay rates, loadings and multipliers are correct in the source systems.
- Award and enterprise agreement interpretation is not performed by this tool.
- Holiday calendars, leave rules and accrual settings are assumed to reflect the organisation’s intended configuration.
- Data quality issues (missing records, duplicates, inconsistent identifiers) may affect the completeness and accuracy of the results.

---

<h2>9. Recommended Next Steps</h2>

1. Validate the highest-severity findings first.
2. Review the most affected modules and confirm whether findings reflect genuine control issues or data limitations.
3. Address structural data gaps that weaken evidentiary confidence.
4. Confirm root causes before remediation.
5. Re-run the review after corrective action to confirm that risk indicators have reduced.

---

<h2 class="page-break-before">10. Appendices</h2>

### Appendix A – Rule Definitions

This review used a set of automated rules to flag evidential and process risk indicators.

#### Leave & Entitlement Leakage

- Negative balance checks
- Casual employees accruing leave
- Inactive or terminated employees with leave movements
- Unusual accrual or usage patterns

#### Long Service Leave (LSL) Exposure

- Inconsistent LSL accrual patterns
- LSL balances inconsistent with service duration
- Missing or incomplete service date records

#### Termination Exposure (TERM)

- Final pay sequencing checks vs termination date
- Missing / inconsistent termination dates
- Missing / inconsistent termination type / reason
- Missing evidence references / artefact identifiers
- Ambiguous identification of final pay events within a window
- Termination events inconsistent with ordinary pay activity patterns

#### Record-Keeping & Evidence Gaps (RKEG)

- Missing employee master data fields
- Orphan pay events and traceability gaps
- Inconsistent employment status records
- Missing or inconsistent termination attributes

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
