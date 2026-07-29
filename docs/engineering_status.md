# Version 1 Engineering Status

## Decision

Version 1 engineering is complete. The Payroll Diagnostics Engine is suitable
for an owner-supervised pilot.

The following reviews and corrective phases are complete:

- Architecture Review;
- Verification Review;
- Enterprise Hardening;
- Acceptance Review and hardening follow-up;
- Rule Quality & False-Positive Review;
- Pilot Safety Corrective Pass.

The architecture is considered stable for the current file-based pilot scope.

---

## Stable engineering contracts

Future work should preserve:

- layered ingestion, diagnostic and reporting boundaries;
- independent module execution;
- configuration-driven rule metadata;
- deterministic finding identity;
- canonical ingestion mapping;
- module-specific validation and provenance;
- structured evidence in findings;
- client/pilot workspace isolation;
- investigative, non-legal report framing.

Architectural change requires a specific demonstrated need. It should not be
introduced as speculative preparation for possible future scale.

---

## Current engineering posture

During Pilot Validation & Rule Calibration:

- minimise production-code changes;
- correct reproducible engineering defects;
- keep defect correction separate from rule calibration;
- preserve public contracts unless evidence requires change;
- require regression tests for runtime changes;
- avoid new frameworks, module redesign or broad refactoring;
- prefer operational learning and reporting clarity over new capability.

The primary work now is:

- controlled client validation;
- rule calibration supported by cross-pilot evidence;
- report interpretation and clarity;
- payroll subject-matter feedback;
- operational experience;
- maintenance of intake, provenance and delivery procedures.

---

## What is not major engineering work remaining

The current phase does not assume the engine needs:

- a new rule framework;
- a new finding model;
- new identity semantics;
- module consolidation;
- automatic suppression of overlapping findings;
- real-time integrations;
- a replacement reporting architecture.

Those may become future product proposals, but only after pilot evidence and a
separate scope decision.

---

## Change classification

Before changing production code, classify the request:

1. **Engineering defect** — implementation violates a stable contract or fails
   at runtime.
2. **Rule calibration** — correctly implemented behaviour needs evidence-backed
   adjustment.
3. **Reporting or operational improvement** — presentation or pilot process
   change with no diagnostic semantic change.
4. **Payroll policy decision** — belongs to the client or product owner.
5. **Legislative interpretation** — requires qualified advice and is outside
   diagnostic engineering.
6. **Future enhancement** — optional capability outside Version 1 validation.

Use the rule calibration process for category 2. Record categories 3 and 6 in
the roadmap or technical debt register rather than silently treating them as
defects.

---

## Related

- [`ROADMAP.md`](ROADMAP.md)
- [`operations/pilot_validation_strategy.md`](operations/pilot_validation_strategy.md)
- [`rules/calibration_process.md`](rules/calibration_process.md)
- [`operations/technical_debt_register.md`](operations/technical_debt_register.md)
- [`contracts/finding_identity_contract.md`](contracts/finding_identity_contract.md)
- [`contracts/ingestion_mapping_contract.md`](contracts/ingestion_mapping_contract.md)
