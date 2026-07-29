# Pilot Readiness Checklist

Status of the items that gate a client pilot. Updated by the Enterprise Pilot
Hardening change set; see `CHANGELOG.md`.

Scope: an 800-employee, file-based pilot with a small number of payroll cycles.
Items marked *Deferred* are known, documented and accepted for that scope.

---

## Correctness

| Item | Status | Evidence |
|---|---|---|
| RKEG findings construct without error across all domains | Done | `tests/rkeg/test_rkeg_finding_construction.py`; a diagnostic run producing EMP, LEAVE and SUP findings |
| Australian dates parse day-first under a declared format | Done | `tests/common/test_date_parsing.py`; ingestion of a day-first pilot |
| Invalid non-null dates stop the run with an actionable message | Done | `tests/common/test_date_parsing.py` |
| Nulls remain acceptable where the canonical model permits them | Done | `tests/common/test_date_parsing.py` |
| Canonical date output format unchanged (`%Y-%m-%d`) | Done | `tests/ingestion/test_ingest_adp_mapping.py` |

## Configuration

| Item | Status | Evidence |
|---|---|---|
| Mapping templates match the ingestion contract and direction | Done | `tests/common/test_mapping_contract.py` |
| Both template copies stay synchronised | Done | `tests/common/test_mapping_contract.py` |
| Mapping is validated before any dataset is read | Done | `src/common/mapping_contract.py`, called from `load_mapping` |
| A non-canonical vendor mapping is proven to work | Done | `templates/examples/adp_column_mapping_example.yaml`, `tests/ingestion/test_ingest_adp_mapping.py` |
| Withdrawn `source` / `columns` shape is rejected, not silently accepted | Done | `tests/common/test_mapping_contract.py` |

## Finding identity

| Item | Status | Evidence |
|---|---|---|
| One documented deterministic ID contract for all modules | Done | `docs/contracts/finding_identity_contract.md` |
| IDs stable across identical reruns | Done | Per-rule rerun tests; a repeated module run producing a byte-identical findings CSV |
| Different employees produce different IDs | Done | `tests/common/test_finding_identity.py` |
| Multiple legitimate findings per employee and rule stay distinguishable | Done | `tests/leave/test_leave_finding_identity.py`, `tests/rkeg/test_rkeg_leave_001.py` |
| Missing or malformed identity evidence fails loudly | Done | `tests/common/test_finding_identity.py` |
| CM-017 and CM-020 no longer collide | Done | `tests/cross_module/test_cross_module_finding_identity.py`; a rerun of the collision case producing 12 distinct IDs from 12 findings |

## Test baseline

| Item | Status | Evidence |
|---|---|---|
| `python -m pytest` collects and runs the supported suite | Done | 240 passed, 1 deselected |
| No stale collection errors | Done | Ten modules rewritten against current interfaces |
| Network-dependent tests explicitly separated | Done | `network` marker, `docs/operations/testing.md` |
| No broad skips or blanket xfail masking failures | Done | One marker on one genuinely external test |

## Provenance and operability

| Item | Status | Evidence |
|---|---|---|
| Ingestion and every diagnostic module write separate manifests | Done | `outputs/run_manifest_{ingestion,leave,lsl,term,rkeg,cross_module}.json`; `tests/common/test_module_manifest_wiring.py` |
| Module execution metadata links to the exact module manifest | Done | `src/common/execution_metadata.py`; production orchestration test |
| Input hashes and row counts recorded | Done | `tests/common/test_run_manifest.py` |
| Configuration hashes and a combined digest recorded | Done | `tests/common/test_run_manifest.py` |
| Git SHA recorded, with a safe fallback | Done | `CRC_GIT_SHA`, then `git rev-parse`, then `unavailable` |
| Python and key dependency versions recorded | Done | `tests/common/test_run_manifest.py` |
| No payroll records or personal data in the manifest | Done | `tests/common/test_run_manifest.py` |
| Documented module CLI commands run on a clean checkout | Done | `scripts/run_*.py` add `src/` to the path |
| Runs survive a non-UTF-8 console | Done | `src/common/console.py` |
| Later HTML/PDF report-package hashing | **Deferred** | Core orchestration outputs are hashed; separate reporting-stage outputs are not yet attached. Section 4 of `docs/operations/run_provenance.md` |
| Historical manifests for repeated runs of the same module | **Deferred** | Module filenames are distinct, but a rerun replaces that module's current manifest |
| Manifest signing or tamper evidence | **Deferred** | Out of scope for a file-based pilot |

## Known limitations accepted for this pilot

| Limitation | Impact | Mitigation |
|---|---|---|
| Row-ordinal identity fallback for extracts with no record identifier | IDs shift if source rows are reordered | Ask the client to supply `transaction_id`; documented in section 4 of the identity contract |
| Unpinned dependencies in `requirements.txt` and `pyproject.toml` | A fresh install may resolve different versions | The manifest records the versions actually used |
| `rkeg.models` and `src.rkeg.models` load as separate modules | Two distinct `Finding` classes exist at runtime | Harmless today because nothing does `isinstance` checks; worth resolving before adding type-based dispatch |
| One current manifest per module | Re-running the same module replaces its prior manifest | Archive delivery manifests externally when run history is required |
| `PILOT_001_2026_03_26` mapping predates the canonical model | That pilot is not re-runnable | Retained as a historical artifact only |

---

## Before each pilot run

1. Confirm the mapping matches the client's actual headers, source column on the
   left.
2. Declare `date_format` if any extract is not ISO.
3. Run `python -m pytest` and confirm a clean result.
4. Run from a Git checkout, or set `CRC_GIT_SHA`, so the code version is recorded.
5. Run ingestion first; it fails fast on a bad mapping or unparseable date.
6. After each run, check its `outputs/run_manifest_{module}.json` records the
   expected inputs, row counts and Git SHA, and that execution metadata names
   the same manifest.
7. Confirm `finding_id` is unique within each findings CSV. A duplicate is a
   defect; see the identity contract.

## Related

- `docs/contracts/ingestion_mapping_contract.md`
- `docs/contracts/finding_identity_contract.md`
- `docs/operations/run_provenance.md`
- `docs/operations/testing.md`
- `docs/operations/client_intake_process.md`
