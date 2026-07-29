# Changelog

Notable changes to CRC. Newest first.

## [Unreleased] — Enterprise Pilot Hardening

Addresses the confirmed pre-pilot blockers from the architecture verification
pass. No architectural redesign.

### Fixed

- **RKEG findings could raise `TypeError`.** The employee, leave and
  superannuation detectors omitted the required `classification` argument when
  constructing a `Finding`, so 15 call sites failed whenever their rule actually
  matched. All 33 RKEG construction sites now go through a single
  `rkeg.models.build_finding` factory, which derives `classification` from the
  rule configuration the way the working PAY, GOV and TERM detectors do.
- **Australian dates were parsed month-first.** Ingestion relied on pandas format
  inference, so `01/02/2024` became 2 January. Dates are now parsed only against
  formats declared in the mapping, defaulting to ISO.
- **Mixed date formats silently nulled valid values.** A column containing both
  ISO and day-first values could lose the ISO values. Non-null values that match
  no declared format now stop the run.
- **Invalid dates were coerced to null with a warning.** Ingestion now fails,
  naming the dataset, column, declared formats and representative offending
  values.
- **Mapping templates contradicted the ingestion code.** `templates/column_mapping_template.yaml`
  and its duplicate documented `source` / `columns` with canonical names on the
  left. Ingestion has always required `source_file` / `rename` with source names
  on the left. Both templates now match the code and are byte-identical.
- **Finding IDs were not deterministic or collision-resistant.**
  - RKEG used `uuid4()`, so every rerun produced different IDs.
  - `CM-017` and `CM-020` omitted `employee_id` from their evidence, collapsing
    every finding for those rules onto one ID per rule. Duplicates existed in
    committed outputs.
  - `RKEG-LEAVE-001` and `LEAVE-014` fire per ledger movement but identified
    movements only by employee, leave type and date, so duplicate movements
    collapsed. They now use `transaction_id`, falling back to the source row
    ordinal.
  - `LEAVE-008` describes a group of duplicate movements but emitted one finding
    per member of the group, all sharing one ID. It now emits one finding per
    group, carrying `occurrence_count` and the contributing transaction IDs.
- **`python -m pytest` executed no tests.** Ten modules failed collection against
  retired interfaces (`rkeg.engine`, `leave_leakage.rules`), which aborted the
  run before any test executed. The default suite now collects and runs.
- **`tests/term/test_term_003.py` passed an argument `prepare_term_state` does not
  accept.**
- **Module CLI scripts could not run without an externally set `PYTHONPATH`.**
  `scripts/run_*.py` added only the repository root, but modules import their
  siblings unprefixed, so `scripts/run_rkeg.py` raised `ModuleNotFoundError`. The
  six pipeline scripts now add `src/` as well.
- **Runs aborted on a default Windows console.** Progress messages containing
  non-ASCII characters raised `UnicodeEncodeError` part way through a successful
  run, which could leave a run without its manifest. Pipeline entry points now
  configure UTF-8 output with replacement.
- **Module metadata could reference ingestion provenance.** Every diagnostic
  orchestration path now writes its own module-specific manifest, and execution
  metadata records that exact filename and the same Git SHA.
- **Finding-ID canonicalisation had delimiter ambiguity.** Identity input is now
  canonical JSON rather than delimiter-joined text, and supplied null, NaN,
  non-finite or blank key values fail clearly.
- **Ingestion could attribute stale processed CSVs to the current run.** Its
  manifest now records only paths written by that execution.

### Added

- `src/common/finding_identity.py` — one deterministic finding-ID contract for
  every module, based on rule code, evidence primary keys and an optional
  discriminator. Raises rather than falling back to a rule-only ID.
- `src/common/date_parsing.py` — explicit date-format resolution and strict
  parsing.
- `src/common/mapping_contract.py` — mapping validation that runs before any
  dataset is read and reports every problem in one pass.
- `src/common/run_manifest.py` — pilot-grade, module-specific run manifests
  written as `outputs/run_manifest_{module}.json`, recording run identity, client and pilot,
  execution mode, input and configuration hashes and row counts, combined
  digests, Git commit SHA, Python version and key dependency versions.
- `src/common/console.py` — UTF-8 console configuration for entry points.
- `rkeg.run.select_rules_by_tier` and `PRODUCTION_TIERS`, extracted from
  `rkeg.run.main` so tier gating is testable.
- `templates/examples/adp_column_mapping_example.yaml` plus fixtures in
  `tests/fixtures/adp/`, demonstrating non-canonical vendor headers and a
  per-dataset date-format override.
- `network` pytest marker, deselected by default, isolating the one
  OpenAI-dependent test.
- Documentation: `docs/contracts/ingestion_mapping_contract.md`,
  `docs/contracts/finding_identity_contract.md`,
  `docs/operations/run_provenance.md`, `docs/operations/testing.md`,
  `docs/operations/pilot_readiness_checklist.md`, and this changelog.
- Tests for date parsing, mapping validation, finding identity, run manifest
  generation and hashing, RKEG finding construction per domain, cross-module
  identity, leave identity, and ADP-shaped ingestion.

### Changed

- `{module}_execution_metadata.csv` gains `git_commit_sha` and `run_manifest`
  columns; both correspond to the module manifest finalised with that metadata.
- Ten stale test modules were rewritten against current interfaces rather than
  deleted. The four RKEG sample-data tests now load the production rule
  configuration and dispatch through `rkeg.detectors.registry`, and
  `test_tier_filtering.py` targets `select_rules_by_tier`.

### Migration

- **Mappings using `source` / `columns` are rejected.** No committed pilot mapping
  used that shape, so no shim is provided. See section 5 of
  `docs/contracts/ingestion_mapping_contract.md`.
- **Non-ISO source dates must declare a format.** Mappings that declare nothing
  keep ISO behaviour, which is what every committed extract supplies.
- **Existing `finding_id` values change.** RKEG IDs were random, and several rules
  had their key sets corrected. The corrective follow-up also moved deterministic
  IDs from delimiter-joined input to canonical JSON to eliminate theoretical
  delimiter collisions. Compare findings on rule code plus business keys across
  this boundary, not on `finding_id`.
- `data/clients/CLT_KAGGLE_TEST/PILOT_001_2026_03_26/config/column_mapping.yaml`
  predates the current canonical model and is retained as a historical artifact
  only. It does not satisfy the contract and is not re-runnable.

### Deferred

- HTML/PDF outputs created by later reporting commands are not yet attached to
  diagnostic module manifests. Core module orchestration outputs are hashed; see
  section 4 of `docs/operations/run_provenance.md`.
- Re-running a module replaces that module's current manifest; append-only
  manifest history remains deferred.
- The row-ordinal identity fallback for extracts with no record identifier means
  IDs shift if source rows are reordered. Documented in section 4 of
  `docs/contracts/finding_identity_contract.md`.
- Unpinned dependencies in `requirements.txt` and `pyproject.toml`, and the
  dual-import path (`rkeg.models` and `src.rkeg.models` load as separate
  modules). Both were raised in the architecture review and are outside this
  change set.
