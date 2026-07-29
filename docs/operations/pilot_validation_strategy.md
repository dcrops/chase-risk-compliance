# Pilot Validation Strategy

## Status and scope

The Payroll Diagnostics Engine is in the **Pilot Validation & Rule
Calibration** phase. Version 1 engineering is complete and suitable for an
owner-supervised, file-based pilot.

This strategy governs controlled engagements used to validate rule quality and
report usefulness. It does not turn diagnostic findings into legal,
entitlement or compliance determinations.

The governing principle is:

> Validate with real payroll data first. Calibrate second.

---

## 1. Objectives

### Validate rule quality

Determine whether each triggered rule identifies a condition that a payroll
specialist considers worth investigating, given the data supplied and the
rule's stated purpose.

### Measure report usefulness

Assess whether operational and executive reports help reviewers:

- understand what triggered;
- locate the supporting evidence;
- prioritise follow-up;
- distinguish a data limitation from a substantive anomaly;
- identify several findings that may share one lifecycle event.

### Identify false positives

Record findings where the implemented rule triggered correctly but the
underlying condition is benign, expected, already controlled or misleading in
the client context.

Do not treat every closed finding as a false positive. A useful diagnostic can
be resolved without identifying an error.

### Identify false negatives

Use targeted payroll-specialist review, known exception samples and client
reconciliation information to identify material conditions the engine did not
surface.

Absence of a finding is not evidence that no issue exists, especially where
optional data was not supplied.

### Collect subject-matter feedback

Capture payroll specialist comments on:

- trigger logic;
- severity and prioritisation;
- evidence sufficiency;
- terminology;
- investigation steps;
- client-specific context;
- missing data dependencies.

---

## 2. Pilot safeguards

1. **Owner review is required.** No report is delivered without review by the
   pilot owner or an explicitly delegated reviewer.
2. **Diagnostics are investigative.** Findings are indicators for review, not
   legal conclusions, confirmed underpayments or determinations of
   non-compliance.
3. **HIGH findings are reviewed before delivery.** Confirm the source evidence,
   rule basis, wording and recommended action for every HIGH finding.
4. **Optional datasets are explicit.** Record which optional datasets were
   supplied, absent or materially incomplete, and explain the resulting
   coverage limitations.
5. **Lifecycle overlap is interpreted.** Review concentrated employees end to
   end. Finding counts are counts of triggered checks, not counts of distinct
   payroll events.
6. **Raw data is preserved.** Follow the client intake process; do not alter
   source extracts.
7. **Run provenance is retained.** Keep the active mappings, rule
   configuration, manifests and delivered outputs for the engagement.
8. **Client-specific facts stay client-specific.** Do not generalise one
   client's policy, process or data shape into a global rule change without
   broader evidence.

---

## 3. Pilot preparation

Before execution:

1. Agree the pilot scope, review period, employee population and included
   modules.
2. Identify supplied and missing datasets.
3. Confirm mappings against the client's actual headers.
4. Record known policy or system behaviours that may affect interpretation.
5. Define the reviewer group, including the payroll subject-matter expert.
6. Select targeted samples for false-negative review, such as known
   terminations, leave adjustments or payroll exceptions.
7. Assign a pilot identifier and evidence register.
8. Complete the pilot readiness checklist.

---

## 4. Execution and review

### Run controls

- Run ingestion before diagnostics.
- Resolve validation errors; retain warnings as coverage notes.
- Run the agreed modules and modes only.
- Confirm manifests identify the expected inputs, configuration and code
  version.
- Confirm finding IDs are unique within each findings output.
- Generate reports from the reviewed run.

### Finding review

For each HIGH finding and a representative sample of MEDIUM and LOW findings:

1. Confirm the rule triggered as implemented.
2. Inspect the cited source records.
3. Record the investigation outcome.
4. Record the time and information needed to reach that outcome.
5. Ask whether the finding was useful even if no error was confirmed.
6. Classify any issue as engineering defect, calibration candidate, policy
   question, legislative interpretation or data limitation.

### False-negative review

Compare engine results to:

- known client exceptions;
- selected employee lifecycle samples;
- payroll specialist concerns;
- relevant reconciliations or control reports supplied for the pilot.

Document any condition that should plausibly have been surfaced but was not.
Do not add a new rule during the pilot review solely because one reviewer can
imagine a scenario.

---

## 5. Evidence to collect

Use a structured evidence register with, at minimum:

| Field | Purpose |
|---|---|
| Pilot and client ID | Engagement traceability |
| Rule code and finding ID | Stable link to the finding |
| Employee/event reference | Link related findings without changing identity |
| Finding severity and classification | Context at the time of review |
| Data coverage | Supplied, missing or incomplete datasets |
| Investigation outcome | Confirmed concern, useful indicator, benign condition, data limitation, unresolved |
| False-positive assessment | Yes/no/uncertain with reason |
| False-negative observation | Description and supporting sample |
| Investigation effort | Minutes/hours and participants |
| Evidence sufficiency | Sufficient, partial or insufficient |
| Payroll specialist comment | Subject-matter feedback |
| Client feedback | Clarity and usefulness |
| Rule confirmed correct | Yes/no/uncertain |
| Adjustment candidate | Threshold, scope, severity, wording, evidence or reporting |
| Proposed rationale | Why a future change may be warranted |
| Decision | No change, monitor, engineering defect, calibration candidate, policy question |

Also collect:

- rules repeatedly confirmed correct;
- rules repeatedly requiring explanation;
- thresholds requiring review;
- wording improvements;
- report sections that need significant clarification;
- missing datasets that materially limited conclusions;
- lifecycle clusters where several findings had one root cause.

---

## 6. Measures

Measure at rule and pilot level where the sample is meaningful:

- findings reviewed;
- findings considered useful;
- confirmed false positives;
- unresolved findings;
- observed false negatives;
- median and range of investigation effort;
- percentage of findings with sufficient evidence;
- percentage of HIGH findings changed or withheld after owner review;
- report clarification requests;
- lifecycle concentration by employee and theme;
- optional-data coverage.

Do not publish a false-positive percentage without also stating the reviewed
sample and outcome definitions.

---

## 7. Success criteria

The engine may progress beyond pilot validation when evidence shows:

1. **False positives are consistently low enough for supervised operational
   use.** The rate is measured on reviewed findings and is not driven by one
   favourable engagement.
2. **Payroll specialists consider findings useful.** Feedback is positive
   across multiple pilots and rules provide a practical investigation starting
   point.
3. **Executive reports are understood without significant clarification.**
   Intended readers can explain the key risks, limitations and concentration
   of findings.
4. **No recurring material engineering defects remain.** Any defect that causes
   crashes, unstable identity, incorrect canonical mapping or materially wrong
   selection logic is corrected and regression-tested.
5. **False-negative review finds no recurring material blind spot** within the
   declared data coverage.
6. **Investigation effort is proportionate.** Evidence and wording let reviewers
   reach an outcome without excessive reconstruction for the value obtained.
7. **Calibration proposals are supported by multiple engagements.** Threshold,
   severity or scope changes show a recurring pattern rather than an isolated
   preference.
8. **Pilot safeguards operate effectively.** Owner review catches ambiguity
   before delivery and coverage limitations are consistently disclosed.

The project owner records the decision to exit pilot validation, including the
pilots considered and any accepted residual limitations.

---

## 8. Pilot close-out

At the end of each engagement:

1. Reconcile all reviewed findings to the evidence register.
2. Summarise false positives, possible false negatives and investigation effort.
3. Record report-clarity and payroll-specialist feedback.
4. Separate engineering defects from calibration candidates.
5. Do not change thresholds during close-out.
6. Add credible calibration candidates to the cross-pilot calibration register.
7. Archive the run artefacts and delivered report according to the agreed
   operating process.

See [`../rules/calibration_process.md`](../rules/calibration_process.md) for how
cross-pilot evidence becomes an approved rule change.
