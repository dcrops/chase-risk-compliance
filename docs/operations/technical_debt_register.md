# Remaining Technical Debt and Deferred Work

## Status

Reviewed at transition to **Pilot Validation & Rule Calibration**.

No known deferred item is a blocker for an owner-supervised, file-based pilot.
The classifications below prioritise work without authorising implementation.

Classification meanings:

- **Pilot blocker** — must be resolved before another controlled client pilot.
- **High priority after pilot** — does not prevent supervised validation, but
  should be addressed before broader or less-supervised operation.
- **Normal backlog** — useful maintenance with an effective pilot mitigation.
- **Future enhancement** — optional capability requiring a separate product
  decision.

---

## Pilot blocker

**None currently identified.**

Any recurring material defect discovered during a pilot—such as a module crash,
incorrect canonical mapping, duplicate finding identity or materially wrong
selection logic—must be reclassified as a pilot blocker until corrected.

---

## High priority after pilot

### Dependency pinning and reproducible environments

- **Current state:** `requirements.txt` and `pyproject.toml` do not fully pin
  dependency versions.
- **Risk:** a fresh installation can resolve versions different from the
  validated environment.
- **Pilot mitigation:** manifests record the dependency versions used and the
  supervised operator runs the supported test suite.
- **Why after pilot:** broader repeatability needs an explicit supported
  environment and lock/update policy.

### Reporting-package provenance

- **Current state:** diagnostic orchestration outputs are hashed, but later
  HTML/PDF packaging is not attached to the originating run manifest.
- **Risk:** a delivered report package is not fully represented by the module
  provenance record.
- **Pilot mitigation:** retain the generated package with the reviewed run and
  archive delivery artefacts operationally.
- **Why after pilot:** report delivery experience should define whether a
  reporting-stage manifest, package digest or delivery manifest is most useful.

### Duplicate import paths

- **Current state:** `rkeg.models` and `src.rkeg.models` can load as separate
  Python modules.
- **Risk:** type identity can differ if future code relies on `isinstance` or
  type-based dispatch.
- **Pilot mitigation:** current paths do not use those checks.
- **Why after pilot:** resolve before adding type-based extension or packaging
  the engine as an installed application.

---

## Normal backlog

### Historical manifest retention

- **Current state:** re-running a module replaces that module's current
  manifest.
- **Pilot mitigation:** archive the final delivery run and its manifests in the
  engagement record.
- **Future decision:** timestamped manifests or an append-only run ledger.

### Row-ordinal finding identity fallback

- **Current state:** a small number of source-record rules use source row order
  when no natural transaction identifier exists.
- **Risk:** equivalent row reordering changes those finding IDs.
- **Pilot mitigation:** request `transaction_id` or another stable record key;
  retain source ordering; follow the finding identity contract.
- **Future decision:** require a canonical record identifier where source
  systems can provide one.

### Rule catalogue coverage

- **Current state:** the dedicated catalogue covers LEAVE; TERM, LSL, RKEG and
  Cross-Module rules are primarily documented in configuration and generated
  reports.
- **Pilot mitigation:** use versioned YAML rule metadata and generated rule
  appendices during review.
- **Future decision:** expand human-readable catalogues based on what payroll
  specialists need during pilots.

### Historical pilot mapping

- **Current state:** `PILOT_001_2026_03_26` predates the canonical mapping model
  and is intentionally retained as a historical artefact.
- **Pilot mitigation:** do not rerun it; create new pilots from the current
  template.
- **Future decision:** none required unless historical reproducibility becomes
  a product requirement.

---

## Future enhancement

### Manifest signing or tamper evidence

- **Current state:** manifests support reproducibility but are editable files.
- **Scope:** signing, immutable storage or non-repudiation.
- **Reason deferred:** not required for supervised file-based validation and
  needs a delivery/security design.

### Automated lifecycle finding suppression or collapse

- **Current state:** executive reporting communicates concentration and overlap;
  underlying findings remain intact.
- **Reason deferred:** suppression could hide useful independent evidence and
  must be supported by pilot outcomes.
- **Decision principle:** prefer presentation and root-cause review until
  repeated pilot evidence demonstrates that specific findings should be merged.

### New modules, integrations and architectural expansion

- **Current state:** Version 1 architecture is stable.
- **Reason deferred:** current priority is validation, calibration, reporting
  clarity and operational learning.
- **Decision principle:** require a separate post-pilot product decision.

### Client-specific configuration profiles

- **Potential scope:** approved client-level context or thresholds.
- **Reason deferred:** premature before pilots establish which differences are
  genuinely client-specific and which indicate shared calibration.

---

## Calibration candidates are not technical debt

Potential threshold, severity, scope or wording changes are tracked through
[`../rules/calibration_process.md`](../rules/calibration_process.md), not this
register.

They become work only when pilot evidence supports a proposal. A speculative
calibration idea is not an engineering defect or backlog commitment.

---

## Review cadence

Review this register:

- at the close of each controlled pilot;
- when a material engineering defect is identified;
- before moving beyond owner-supervised operation;
- before approving architectural or packaging work.
