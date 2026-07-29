# Termination Exposure – Final Pay Identification Contract (v1)

## Scope
- Files: `terminations.csv`, `pay_events.csv`, `employees.csv` (optional)
- Purpose: evidence of termination pay traceability, not entitlement correctness.

## Date Parsing Rules
- Accepted formats: YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY
- Unparseable dates are excluded from timing-based rules.

## Definitions
- Termination event
- Pay event
- Pay on/after termination
- Explicit final pay flag (`is_final_pay`)
- Last ordinary pay before termination
- Gap calculation (`gap_days`)
- Ambiguous final pay window (−14, +30 days)
- Thresholds:
  - `MAX_FINAL_PAY_GAP_DAYS = 35`
  - `AMBIGUOUS_WINDOW_BEFORE_DAYS = 14`
  - `AMBIGUOUS_WINDOW_AFTER_DAYS = 30`

## Rule Mapping
- TERM-001 uses: pay on/after termination
- TERM-002 uses: explicit final pay flag before termination
- TERM-003 uses: last ordinary pay + `MAX_FINAL_PAY_GAP_DAYS`
- TERM-006 uses: ambiguity window + explicit final pay flag
- RKEG-TERM-001 uses: preferred `is_final_pay` on or after termination; falls
  back to the latest post-termination pay only when no flagged final pay exists,
  and records `final_pay_basis` in the evidence (`flagged_final_pay` or
  `latest_post_termination_pay`). The configured day threshold is a diagnostic
  review trigger, not a statutory test.

## Evidence references
- Canonical termination evidence field: `evidence_reference`
- Supported legacy aliases (intentional fallbacks only): `evidence_ref`,
  `termination_evidence`, `document_id`
- Shared resolver: `src/common/evidence_fields.py` (used by TERM-005 and
  Cross-Module evidence-dependent checks)

## Lifecycle interpretation for pilots
- Finding counts are counts of triggered checks, not counts of distinct payroll
  events. One termination can raise findings across TERM, LEAVE, RKEG and
  Cross-Module Integrity.
- The executive pack reports lifecycle concentration by employee and theme so
  that volume is read in context. Findings are not suppressed or merged.