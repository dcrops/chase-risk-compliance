# Payroll Diagnostics Engine Roadmap

## Current status

Version 1 engineering is complete. The deterministic architecture, module
boundaries, finding identity contract, ingestion contract and reporting
pipeline are considered stable for an owner-supervised pilot.

The project is now in **Pilot Validation & Rule Calibration**.

Operating principle:

> Validate with real payroll data first. Calibrate second.

Future rule changes must be supported by evidence from controlled pilot
engagements. The roadmap does not assume that more engineering or more rules
will improve the engine.

---

## Completed phases

### 1. Architecture Review — Complete

- Reviewed module boundaries, orchestration and reporting structure.
- Confirmed the layered, deterministic architecture.
- Identified hardening requirements without redesigning the engine.

### 2. Verification Review — Complete

- Verified implementation paths against documented behaviour.
- Confirmed supported execution modes and output contracts.

### 3. Enterprise Hardening — Complete

- Standardised deterministic finding identity.
- Strengthened mapping and date parsing contracts.
- Added module-specific provenance and executable test coverage.
- Improved operational reliability on supported pilot environments.

### 4. Acceptance Review and Hardening Follow-up — Complete

- Re-tested corrected contracts and module execution.
- Closed material acceptance blockers.

### 5. Rule Quality & False-Positive Review — Complete

- Reviewed diagnostic logic, evidence sufficiency, wording and false-positive
  exposure.
- Assessed cross-module overlap and controlled pilot outputs.
- Concluded: **Pass with pilot safeguards**.

### 6. Pilot Safety Corrective Pass — Complete

- Corrected canonical termination evidence handling.
- Improved final-pay identification and diagnostic wording.
- Corrected LSL service duration and invalid-date handling.
- Corrected latest-snapshot selection in termination and lifecycle rules.
- Aligned CM-019 with its configured meaning.
- Added lifecycle concentration reporting without suppressing findings.
- Added pilot-critical regression tests and updated contracts.

Outcome: **Suitable for an owner-supervised pilot**.

---

## Current phase: Pilot Validation & Rule Calibration

### Purpose

Validate Version 1 against controlled client payroll data and establish which
rules, thresholds and report wording are useful in practice.

### Activities

- Conduct controlled client pilots with owner review.
- Record false positives and their causes.
- Look for plausible false negatives through targeted sample review.
- Measure the effort required to investigate each finding.
- Assess whether report wording and evidence are clear.
- Validate whether executive reporting supports prioritisation and discussion.
- Gather structured feedback from payroll subject-matter experts.
- Refine thresholds only where evidence from multiple engagements supports a
  change.

### Outputs

- Pilot evidence register.
- Rule-level validation results.
- False-positive and false-negative observations.
- Investigation-effort measures.
- Payroll specialist and client feedback.
- Report clarity findings.
- Evidence-backed calibration proposals.

---

## Engineering corrections versus rule calibration

### Engineering correction

An engineering correction makes implementation conform to an existing,
defensible contract or prevents incorrect runtime behaviour.

Examples:

- a detector reads the wrong canonical field;
- an invalid input crashes a module instead of producing a finding;
- a finding identity is unstable or duplicated;
- historical data is selected in the wrong order;
- configured behaviour and implementation do not match.

Engineering defects may be corrected when reproduced and tested. They do not
require several pilots if the contract and defect are unambiguous.

### Rule calibration

Calibration changes how a correctly implemented rule identifies or
communicates risk.

Examples:

- changing a materiality threshold;
- changing a timing window;
- altering severity based on observed usefulness;
- refining wording to reduce repeated misunderstanding;
- changing rule scope because benign scenarios recur.

Calibration requires pilot evidence. An isolated observation is not enough to
change a threshold or generalise business meaning.

### Not calibration

The following require separate ownership and must not be presented as engine
calibration:

- payroll policy decisions;
- award, agreement or contract interpretation;
- legislative interpretation;
- legal conclusions;
- client-specific risk acceptance.

See:

- [`operations/pilot_validation_strategy.md`](operations/pilot_validation_strategy.md)
- [`rules/calibration_process.md`](rules/calibration_process.md)
- [`operations/technical_debt_register.md`](operations/technical_debt_register.md)

---

## Later phases

### Post-pilot calibration release

Begins only when the success criteria in the pilot validation strategy are met.
Its scope is limited to evidence-backed changes accepted through the calibration
process.

### Future enhancement

Product expansion, new modules, integrations and architectural changes are not
part of the current phase. They require a separate decision after pilot
validation and must not displace rule-quality learning.
