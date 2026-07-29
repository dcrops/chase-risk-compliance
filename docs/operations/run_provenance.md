# Run Provenance (v1)

What a completed run records about itself, so a finding can be traced back to the
inputs, configuration and code that produced it.

Implemented by `src/common/run_manifest.py`.

This is a deliberately bounded first version, not a provenance subsystem. Read
section 4 before relying on it for audit evidence.

---

## 1. Location

Every production orchestration path writes a separate JSON manifest:

```
outputs/run_manifest_ingestion.json
outputs/run_manifest_leave.json
outputs/run_manifest_lsl.json
outputs/run_manifest_term.json
outputs/run_manifest_rkeg.json
outputs/run_manifest_cross_module.json
```

Running one module never overwrites another module's manifest. Re-running the
same module replaces that module's prior manifest, because this bounded version
retains current provenance rather than run history.

Each diagnostic module also records `git_commit_sha` and its exact manifest
filename in `outputs/{module}_execution_metadata.csv`. The metadata and manifest
are finalised together, so a module cannot claim provenance from ingestion's
manifest.

---

## 2. Fields

### Run identity

| Field | Notes |
|---|---|
| `manifest_version` | Schema version, currently `1.0` |
| `run_id` | Random hex, unique per run. Identifies the run, not its content |
| `generated_at_utc` | ISO 8601 UTC timestamp |
| `client`, `pilot` | Identifiers where available |
| `execution_mode` | e.g. `ingestion`, `full`, `payroll_only` |
| `module` | e.g. `INGESTION`, `RKEG` |

### Code and environment

| Field | Notes |
|---|---|
| `git_commit_sha` | See section 3 |
| `python_version` | e.g. `3.13.5` |
| `platform` | OS name and release |
| `dependency_versions` | `pandas`, `numpy`, `pyyaml`, `jinja2`, `weasyprint`, `markdown`; absent packages record `not installed` |

### Inputs, configuration, outputs

Each entry records `path` (relative to the pilot directory), `sha256`,
`size_bytes` and `row_count` (data rows excluding the header; `null` for non-CSV).

| Field | Notes |
|---|---|
| `inputs` | Ingestion: every source file named by the mapping. Modules: processed files actually loaded by that module |
| `inputs_combined_sha256` | Order-independent digest of the input hashes |
| `config_files` | Ingestion: active `column_mapping.yaml`. Modules: active rule configuration |
| `config_combined_sha256` | Order-independent digest of the configuration hashes |
| `outputs` | Generated files, where the caller supplies paths (section 4) |
| `outputs_combined_sha256` | Order-independent digest of the output hashes |
| `notes` | Machine-readable statement of the limitations below |

The combined digests are the practical comparison point: identical
`inputs_combined_sha256` plus identical `config_combined_sha256` plus identical
`git_commit_sha` means the run should be reproducible.

### Privacy

The manifest records **file digests and row counts only**. It never contains
payroll records, employee identifiers, or any other personal information.
Enforced by `tests/common/test_run_manifest.py`.

---

## 3. Git SHA discovery

Resolved in order:

1. the `CRC_GIT_SHA` environment variable, for packaged or exported runs that
   want to record their provenance explicitly;
2. `git rev-parse HEAD` in the repository;
3. the literal string `unavailable`.

A missing SHA never fails a run. A packaged run, an exported copy, a machine with
no `git` binary, and a directory that is not a repository all resolve to
`unavailable` rather than raising.

`unavailable` means "the code version was not recorded", so such a run is not
evidence of which code produced it. For pilot delivery, either run from a
checkout or set `CRC_GIT_SHA`.

---

## 4. Limitations of this version

Stated explicitly so the design is not ambiguous.

1. **Output hashing covers orchestration outputs, not later report packaging.**
   Ingestion records exactly the canonical files written by that execution and
   excludes unrelated stale files already in `processed/`. Diagnostic modules
   record their CSV/Markdown orchestration outputs and execution metadata.
   Separate reporting commands that later produce HTML/PDF packs are not yet
   attached to the originating module manifest.
2. **One current manifest per module.** Different modules do not overwrite each
   other, but re-running the same module replaces its previous manifest. Retaining
   historical manifests or an append-only run ledger remains deferred.
3. **`run_id` does not identify content.** It is random per run. Use the combined
   digests to compare runs.
4. **Reporting-stage provenance is separate.** The five diagnostic orchestration
   paths hash their active rule files. Post-processing by `src/reporting` is not
   currently represented as its own manifest.
5. **No signing or tamper evidence.** The manifest sits beside the outputs it
   describes and can be edited like any other file. It supports reproducibility,
   not non-repudiation.

---

## 5. Reading a manifest

```bash
python -c "import json; print(json.dumps(json.load(open('data/clients/CLT/PILOT/outputs/run_manifest_rkeg.json')), indent=2))"
```

Or from Python:

```python
from common.run_manifest import read_manifest
manifest = read_manifest(
    "data/clients/CLT/PILOT/outputs",
    "run_manifest_rkeg.json",
)
print(manifest["git_commit_sha"], manifest["inputs_combined_sha256"])
```

To confirm two runs consumed the same data, compare `inputs_combined_sha256`,
`config_combined_sha256` and `git_commit_sha`. If all three match and the
findings differ, the difference comes from something outside the manifest's
coverage — investigate rather than assume.

---

## 6. Related

- `docs/contracts/ingestion_mapping_contract.md`
- `docs/contracts/finding_identity_contract.md`
- `docs/operations/pilot_readiness_checklist.md`
