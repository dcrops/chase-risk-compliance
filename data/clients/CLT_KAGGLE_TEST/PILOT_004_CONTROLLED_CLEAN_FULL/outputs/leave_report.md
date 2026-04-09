# Leave & Entitlement Leakage – Detailed Report

**Organisation:** Organisation name not provided  
**Review period:** 15 Mar 2024 to 10 Apr 2024  
**Report prepared as at:** 09 Apr 2026  

**Important note**

This report highlights potential risk signals and process issues based on the data provided.  
It does not constitute legal, accounting, or industrial relations advice.

---

<h2 class="page-break-before">1. Executive Summary</h2>

This Leave & Entitlement Leakage report focuses solely on leave-related risk indicators identified from the supplied payroll and HR data. Findings are risk indicators only and do not, on their own, confirm underpayment, non-compliance, or an entitlement error.

Across the dataset provided, the automated checks identified:

- **High:** 2
- **Medium:** 0
- **Low:** 0

A detailed breakdown by severity is provided in the **Findings Overview** section.

No exposure estimates were available from the current data extract. If required, leakage estimates can be added to this section in future runs.

---

<h2 class="page-break-before">2. Data Sources</h2>

This review was generated from the following analysis outputs within the project `outputs/` directory:

- `leave_leakage_findings.csv`  
- `leakage_report.csv`  
- `executive\executive_summary.md`  
- `executive\executive_summary.json`  
- `crc_coverage_insight.md`  

These outputs were produced by rule-based checks over payroll and HR CSV extracts supplied by the organisation for the review period.

---

<h2 class="page-break-before">3. Scope & Methodology</h2>

**Modules included in this engagement:**

- Leave & Entitlement Leakage (LEAVE)

---

### **Leave & Entitlement Leakage – Scope & Methodology**

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

<h2>4. Findings Overview</h2>

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

<h2>5. Detailed Findings</h2>

This section sets out detailed findings for **leave and entitlement leakage** only. Record-Keeping & Evidence Gaps (RKEG) and Termination Exposure findings are available in machine-readable form (see Appendix C) and are intended to support operational review, sampling and remediation planning rather than narrative reporting.

Each leave finding below follows a consistent **Finding → Evidence → Impact → Recommended Action** pattern.

### Finding 1: LEAVE-007
**Severity:** HIGH

**Finding**
Leave transactions were recorded after the employee termination date.

**Evidence**

- Employee ID: `E002`
- Leave type: `ANNUAL`
- As at: `2024-04-10`

**Impact / Risk**
Potential leave or entitlement imbalance and/or record-keeping weakness. The actual impact will depend on the underlying award or agreement, actual pay outcomes, and the period over which the issue has occurred.

**Recommended Action**

- Validate this finding against source payroll records and employee entitlements.
- Correct any confirmed configuration, data or process issues.
- Consider remediation where underpayments are confirmed.

### Finding 2: LEAVE-007
**Severity:** HIGH

**Finding**
Leave transactions were recorded after the employee termination date.

**Evidence**

- Employee ID: `E005`
- Leave type: `ANNUAL`
- As at: `2024-03-15`

**Impact / Risk**
Potential leave or entitlement imbalance and/or record-keeping weakness. The actual impact will depend on the underlying award or agreement, actual pay outcomes, and the period over which the issue has occurred.

**Recommended Action**

- Validate this finding against source payroll records and employee entitlements.
- Correct any confirmed configuration, data or process issues.
- Consider remediation where underpayments are confirmed.

---

<h2>6. Financial Exposure (Indicative)</h2>

No exposure estimates were available from the current data extract. If required, leakage estimates can be added to this section in future runs.

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

#### Leave & Entitlement Leakage

- Negative balance checks
- Casual employees accruing leave
- Inactive or terminated employees with leave movements
- Unusual accrual or usage patterns

---

### Appendix B – Machine-readable outputs

Complete machine-readable outputs are available in the generated CSV and summary files for the modules included in this engagement.

These files provide row-level detail suitable for operational review, sampling, remediation planning, or incorporation into a broader audit work program.

---
