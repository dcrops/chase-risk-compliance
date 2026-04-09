# Cross-Module Integrity – Detailed Report

**Organisation:** Organisation name not provided  
**Review period:** 01 Mar 2024 to 20 Apr 2024  
**Report prepared as at:** 09 Apr 2026  

**Important note**

This report highlights potential risk signals and process issues based on the data provided.  
It does not constitute legal, accounting, or industrial relations advice.

---

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

Each finding below follows a consistent **Finding → Evidence → Impact / Risk → Recommended Action** pattern.

### Finding 1: CM-003
**Severity:** HIGH

**Finding**
A termination record has no supporting evidence reference and payroll activity continues after the termination date.

**Evidence**

- Employee ID: `E002`
- As at: `2024-04-20`
- Classification: `LOGICAL`
- Evidence reference: `{"sources": ["terminations.csv", "pay_events.csv"], "primary_keys": {"employee_id": "E002", "termination_date": "2024-03-01", "pay_date": "2024-04-20"}, "values": {"evidence_reference": null, "days_after_termination": 50, "gross_amount": 2500.0}, "thresholds": {"allowed_days_after_term": 14, "high_severity_cutoff_days": 30}, "explanation": "Termination evidence reference is missing and payroll activity continues significantly after termination, indicating a likely lifecycle control breakdown."}`
- Finding ID: `51bf850dc85e`
- Suggested next action (from data): `Review termination evidence records and confirm whether payroll activity after termination was valid or requires correction.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 2: CM-006
**Severity:** HIGH

**Finding**
Payroll activity and leave ledger movement both continue after the employee termination date.

**Evidence**

- Employee ID: `E002`
- As at: `2024-04-10`
- Classification: `LOGICAL`
- Evidence reference: `{"sources": ["terminations.csv", "pay_events.csv", "leave_ledger.csv"], "primary_keys": {"employee_id": "E002", "termination_date": "2024-03-01"}, "values": {"has_post_term_payroll_activity": true, "has_post_term_leave_activity": true, "latest_post_term_leave_date": "2024-04-10", "max_days_after_termination_pay": 50}, "thresholds": {"allowed_days_after_term": 14, "high_severity_cutoff_days": 30}, "explanation": "Payroll activity and leave ledger movement both continue significantly after termination, indicating a likely breakdown in off-boarding control integrity."}`
- Finding ID: `1ba6ace90e24`
- Suggested next action (from data): `Review the employee termination timeline, payroll activity, and leave transactions to confirm whether the employee was correctly finalised.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 3: CM-017
**Severity:** HIGH

**Finding**
A final pay event was flagged but no termination evidence reference exists.

**Evidence**

- Employee ID: `E002`
- As at: `2024-03-05`
- Classification: `LOGICAL`
- Evidence reference: `{"issue": "final pay without evidence", "evidence_reference": null}`
- Finding ID: `061dc6f73892`
- Suggested next action (from data): `Ensure termination evidence such as resignation or termination documentation is recorded and linked to payroll records.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 4: CM-017
**Severity:** HIGH

**Finding**
A final pay event was flagged but no termination evidence reference exists.

**Evidence**

- Employee ID: `E005`
- As at: `2024-03-10`
- Classification: `LOGICAL`
- Evidence reference: `{"issue": "final pay without evidence", "evidence_reference": null}`
- Finding ID: `061dc6f73892`
- Suggested next action (from data): `Ensure termination evidence such as resignation or termination documentation is recorded and linked to payroll records.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 5: CM-020
**Severity:** HIGH

**Finding**
An employee triggered multiple cross-module integrity failures.

**Evidence**

- Employee ID: `E002`
- Classification: `CONTEXTUAL`
- Evidence reference: `{"total_findings": 6, "high_findings": 3, "thresholds": {"min_findings": 3, "min_high_severity": 2}, "explanation": "The employee triggered multiple cross-module integrity failures, including multiple high-severity signals, indicating a likely systemic lifecycle control breakdown."}`
- Finding ID: `050e64ad6d2a`
- Suggested next action (from data): `Review the full lifecycle of the employee including payroll, leave, termination and evidence records.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 6: CM-002
**Severity:** MEDIUM

**Finding**
Leave ledger movement was recorded after the employee termination date.

**Evidence**

- Employee ID: `E002`
- Related record / leave type: `ANNUAL`
- As at: `2024-04-10`
- Classification: `CONTEXTUAL`
- Evidence reference: `{"sources": ["terminations.csv", "leave_ledger.csv"], "primary_keys": {"employee_id": "E002", "termination_date": "2024-03-01", "event_date": "2024-04-10", "leave_type": "ANNUAL"}, "values": {"event_type": null, "units": 8.0}, "explanation": "Leave ledger movement was recorded after the employee termination date."}`
- Finding ID: `0b7e46d4abc1`
- Suggested next action (from data): `Review termination timing and leave processing history to confirm whether the movement is valid and properly evidenced.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 7: CM-002
**Severity:** MEDIUM

**Finding**
Leave ledger movement was recorded after the employee termination date.

**Evidence**

- Employee ID: `E005`
- Related record / leave type: `ANNUAL`
- As at: `2024-03-15`
- Classification: `CONTEXTUAL`
- Evidence reference: `{"sources": ["terminations.csv", "leave_ledger.csv"], "primary_keys": {"employee_id": "E005", "termination_date": "2024-03-01", "event_date": "2024-03-15", "leave_type": "ANNUAL"}, "values": {"event_type": null, "units": 4.0}, "explanation": "Leave ledger movement was recorded after the employee termination date."}`
- Finding ID: `3f3de4c61b56`
- Suggested next action (from data): `Review termination timing and leave processing history to confirm whether the movement is valid and properly evidenced.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 8: CM-012
**Severity:** MEDIUM

**Finding**
Leave ledger activity was recorded after the employee termination date.

**Evidence**

- Employee ID: `E002`
- Related record / leave type: `ANNUAL`
- As at: `2024-04-10`
- Classification: `CONTEXTUAL`
- Evidence reference: `{"sources": ["leave_ledger.csv", "terminations.csv"], "primary_keys": {"employee_id": "E002", "termination_date": "2024-03-01", "event_date": "2024-04-10", "leave_type": "ANNUAL"}, "values": {"event_type": "nan", "units": 8.0, "days_after_termination": 40}, "thresholds": {"allowed_event_types": ["ADJUSTMENT", "PAYOUT"]}, "explanation": "Leave ledger activity was recorded after the employee termination date."}`
- Finding ID: `ca37a32075d0`
- Suggested next action (from data): `Confirm whether the employee was reinstated or whether the ledger events were posted incorrectly.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 9: CM-012
**Severity:** MEDIUM

**Finding**
Leave ledger activity was recorded after the employee termination date.

**Evidence**

- Employee ID: `E005`
- Related record / leave type: `ANNUAL`
- As at: `2024-03-15`
- Classification: `CONTEXTUAL`
- Evidence reference: `{"sources": ["leave_ledger.csv", "terminations.csv"], "primary_keys": {"employee_id": "E005", "termination_date": "2024-03-01", "event_date": "2024-03-15", "leave_type": "ANNUAL"}, "values": {"event_type": "nan", "units": 4.0, "days_after_termination": 14}, "thresholds": {"allowed_event_types": ["ADJUSTMENT", "PAYOUT"]}, "explanation": "Leave ledger activity was recorded after the employee termination date."}`
- Finding ID: `d73511e58fab`
- Suggested next action (from data): `Confirm whether the employee was reinstated or whether the ledger events were posted incorrectly.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 10: CM-016
**Severity:** MEDIUM

**Finding**
A termination record exists but no supporting leave snapshot record was identified for the employee.

**Evidence**

- Employee ID: `E002`
- As at: `2024-03-01`
- Classification: `STRUCTURAL`
- Evidence reference: `{"sources": ["terminations.csv", "balances_snapshot.csv"], "primary_keys": {"employee_id": "E002", "termination_date": "2024-03-01"}, "values": {"leave_snapshot_record_found": false}, "thresholds": {"leave_types_checked": ["ANNUAL", "LSL"]}, "explanation": "A termination record exists but no supporting leave snapshot record was identified for the employee."}`
- Finding ID: `ca93e3ef4ed9`
- Suggested next action (from data): `Review snapshot extract completeness and confirm whether terminated employees were intentionally excluded or whether leave balances were missing from the extract.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 11: CM-016
**Severity:** MEDIUM

**Finding**
A termination record exists but no supporting leave snapshot record was identified for the employee.

**Evidence**

- Employee ID: `E005`
- As at: `2024-03-01`
- Classification: `STRUCTURAL`
- Evidence reference: `{"sources": ["terminations.csv", "balances_snapshot.csv"], "primary_keys": {"employee_id": "E005", "termination_date": "2024-03-01"}, "values": {"leave_snapshot_record_found": false}, "thresholds": {"leave_types_checked": ["ANNUAL", "LSL"]}, "explanation": "A termination record exists but no supporting leave snapshot record was identified for the employee."}`
- Finding ID: `81c9d3c56fec`
- Suggested next action (from data): `Review snapshot extract completeness and confirm whether terminated employees were intentionally excluded or whether leave balances were missing from the extract.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

### Finding 12: CM-020
**Severity:** MEDIUM

**Finding**
An employee triggered multiple cross-module integrity failures.

**Evidence**

- Employee ID: `E005`
- Classification: `CONTEXTUAL`
- Evidence reference: `{"total_findings": 4, "high_findings": 1, "thresholds": {"min_findings": 3, "min_high_severity": 2}, "explanation": "The employee triggered multiple cross-module integrity failures, indicating a clustered lifecycle control issue that should be reviewed in context."}`
- Finding ID: `050e64ad6d2a`
- Suggested next action (from data): `Review the full lifecycle of the employee including payroll, leave, termination and evidence records.`

**Impact / Risk**
Potential data integrity, sequencing, or lifecycle mismatch across related payroll datasets. These issues may reduce confidence in linked records and make payroll outcomes or employee status changes harder to explain, validate, or reconcile.

**Recommended Action**

- Validate this finding across the linked payroll, employee, leave, and termination records.
- Confirm whether the inconsistency reflects a true process issue, timing difference, or source-system mismatch.
- Correct any confirmed data alignment or lifecycle sequencing issues in the relevant systems.
- Where repeated patterns are identified, strengthen integration, mapping, and reconciliation controls.

---

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
