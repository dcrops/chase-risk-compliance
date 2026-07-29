# Rule Calibration Process

## Purpose

This process governs changes to diagnostic thresholds, timing windows,
severity, scope and wording after Version 1.

Calibration is not speculative rule improvement. It is a controlled response to
evidence collected during pilot engagements.

> Validate with real payroll data first. Calibrate second.

---

## 1. Classify the issue before changing anything

Every proposed change must be assigned one category.

### Engineering defect

The implementation violates an existing contract or behaves incorrectly.

Examples:

- reading a non-canonical field when the canonical field is present;
- crashing on an input the rule is intended to report;
- unstable or duplicate finding identity;
- selecting a historical row instead of the latest row;
- implementation and configuration describing different behaviour.

Engineering defects require reproducible evidence and regression tests. They
are corrected as defects, not justified as calibration.

### Rule calibration

The rule works as designed, but pilot evidence shows that its threshold,
severity, scope, evidence or wording should change to improve diagnostic value.

Examples:

- a timing window repeatedly catches expected processing delays;
- a materiality threshold is too sensitive across several pilots;
- severity does not match investigation priority;
- wording is repeatedly misunderstood;
- a benign scenario needs a defensible exclusion.

### Payroll policy decision

The client must decide how its payroll process should operate. The engine must
not encode one client's preference as a general rule without an explicitly
approved product requirement and supporting evidence.

### Legislative interpretation

The proposal depends on interpreting legislation, an award, an enterprise
agreement, a contract or jurisdiction-specific obligation. This requires
qualified advice and is outside diagnostic calibration.

### Data or coverage issue

The finding is driven by missing, incomplete, poorly mapped or unavailable
data. Improve intake, mapping or coverage disclosure before changing the rule.

---

## 2. Minimum evidence for calibration

A calibration proposal should normally include:

- evidence from more than one controlled pilot engagement;
- the affected rule code and current configuration;
- reviewed finding counts and sample size;
- false-positive or usefulness outcomes with definitions;
- representative benign and concerning examples;
- payroll specialist comments;
- data coverage for each example;
- investigation-effort impact;
- expected effect on false negatives;
- affected reporting and documentation;
- rationale for changing the shared rule rather than using client context.

One observation may create a candidate. It should not normally change a
threshold.

An exception requires a written reason, such as a clearly unsafe wording issue
or evidence that the current calibration systematically misstates what the rule
does. If the issue is actually a defect, classify it as one.

---

## 3. Calibration register

Maintain one cross-pilot register. Each candidate should record:

| Field | Description |
|---|---|
| Candidate ID | Stable reference |
| Rule code | Affected rule |
| Change type | Threshold, timing, severity, scope, exclusion, wording, evidence, reporting |
| Current behaviour | What the rule does now |
| Proposed behaviour | Exact proposed change |
| Pilot evidence | Engagements and reviewed findings |
| Data coverage | Relevant supplied and missing datasets |
| False-positive evidence | Counts, rates and reasons |
| False-negative risk | Expected effect and validation approach |
| SME feedback | Named role and summary |
| Investigation effort | Current and expected effort |
| Policy/legal dependency | None, policy, legislative or unresolved |
| Decision | Observe, reject, approve for implementation |
| Decision rationale | Evidence supporting the decision |
| Validation plan | Tests and post-change pilot comparison |

Client payroll records and personal information must remain in the controlled
engagement workspace, not in general project documentation.

---

## 4. Review gates

### Gate 1 — Evidence sufficiency

Confirm:

- the issue recurs or has a compelling documented exception;
- samples are not all from one data-quality failure;
- optional-data limitations are understood;
- the observed outcome matches the rule's intended purpose.

### Gate 2 — Category and ownership

Confirm the proposal is calibration rather than:

- an engineering defect;
- a client policy choice;
- legislative interpretation;
- a mapping or coverage issue.

Escalate policy and legislative questions to the appropriate owner. Do not
resolve them by editing the rule.

### Gate 3 — Impact analysis

Assess:

- false-positive reduction;
- potential false-negative increase;
- severity and prioritisation effects;
- cross-rule and cross-module interactions;
- finding identity implications;
- report wording;
- backwards comparison of pilot outputs.

Finding identity should remain unchanged unless the grain of the finding
changes. Any identity change must follow the identity contract and be called out
as a compatibility boundary.

### Gate 4 — Approval

The project owner approves:

- the exact configuration or wording change;
- the evidence and rationale;
- the test and documentation plan;
- whether existing pilot outputs require re-evaluation.

---

## 5. Implementation requirements

An approved calibration change must:

1. be minimal and limited to the affected rule or reporting text;
2. preserve architecture and public contracts unless the approved evidence
   requires otherwise;
3. update configuration, detector wording and catalogue text consistently;
4. add positive and negative regression tests;
5. document the evidence-based rationale without including client-identifiable
   information;
6. record the change in the changelog;
7. run the full validation suite;
8. compare representative pre-change and post-change outcomes;
9. state any expected finding-ID compatibility impact.

Do not bundle unrelated calibration candidates into one change.

---

## 6. Post-change validation

After implementation:

- re-run the rule against representative de-identified pilot cases;
- confirm the intended false positives no longer trigger;
- confirm material concerning cases still trigger;
- inspect cross-module concentration and duplicate identity;
- review report wording with a payroll specialist;
- monitor the next controlled pilot for unintended effects.

If evidence remains mixed, revert the proposal to **observe** rather than
continuing to tune it.

---

## 7. Decision principles

- Prefer no change when the evidence is weak.
- Do not optimise to one client.
- Do not lower a false-positive rate by hiding plausible material conditions.
- Do not use severity to imply legal certainty.
- Do not treat thresholds as legislative rules unless qualified interpretation
  has explicitly established that requirement and the product scope accepts it.
- Prefer clearer evidence and wording before adding exclusions.
- Keep calibration traceable to the pilots that justified it.
