# CRC Client Intake Process

## 1. Data Intake (Google Drive)

- Client provides CSV extracts (or files are uploaded manually)
- Files are stored in Google Drive under:


01_INBOUND_RAW/{CLIENT}/{PILOT}


- These files are treated as the **source of truth**
- Raw files are **never modified**

---

## 2. Local Processing Setup

Data is copied from Google Drive into the local project:


data/clients/{CLIENT}/{PILOT}/raw/


This is the working input directory for ingestion.

---

## 3. Mapping Configuration

Column mappings are defined per client/pilot in:


data/clients/{CLIENT}/{PILOT}/config/column_mapping.yaml


This file controls how raw datasets are transformed into standard CRC datasets.

The schema, mapping direction, required datasets, date-format declarations and
validation behaviour are specified in
[`docs/contracts/ingestion_mapping_contract.md`](../contracts/ingestion_mapping_contract.md).
Start from `templates/column_mapping_template.yaml`, or
`templates/examples/adp_column_mapping_example.yaml` for a worked example with
non-canonical vendor headers.

Two points that catch people out:

- The rename direction is **source column on the left, canonical column on the
  right**.
- Dates are parsed only against declared formats. If an extract is not ISO
  (`%Y-%m-%d`), declare `date_format` — otherwise the run fails rather than
  guessing.

---

## 4. Ingestion

The ingestion process:

- Validates `config/column_mapping.yaml` **before reading any dataset**, reporting
  every problem in one pass
- Reads raw input files from `raw/`
- Applies column mappings from `config/column_mapping.yaml`
- Parses dates against the declared formats, failing on any non-null value that
  does not match
- Writes a run manifest to `outputs/run_manifest_ingestion.json`
  (see [`docs/operations/run_provenance.md`](run_provenance.md))
- Outputs standardised datasets to:


processed/


### Example outputs:

- `employees.csv`
- `leave_ledger.csv`
- `leave_balances.csv`
- `leave_requests.csv`
- `pay_events.csv`
- `payroll_transactions.csv`
- `terminations.csv`
- `timesheets.csv`

---

## 5. Module Execution (Next Phase)

Processed datasets are used by CRC modules:

- LEAVE (Leave & Entitlement Leakage)
- TERM (Termination Integrity)
- RKEG (Record Keeping & Evidence Gaps)

Outputs from modules are written to:


outputs/

Each module also writes `run_manifest_{module}.json`; its execution metadata
records that exact filename.

---

## 6. Reporting

Reports are generated in stages:

- Markdown → HTML → PDF

Final outputs are:

- Stored locally in `outputs/`
- Uploaded to Google Drive:


03_OUTPUT_REPORTS/{CLIENT}/{PILOT}


---

## 7. Key Principles

- Raw data is **never modified**
- Ingestion is **fully repeatable** from:
  - `raw/`
  - `config/column_mapping.yaml`
- Every run records what it consumed in its own
  `outputs/run_manifest_{module}.json`
- Findings carry deterministic IDs, so an unchanged rerun reproduces them exactly
  (see [`docs/contracts/finding_identity_contract.md`](../contracts/finding_identity_contract.md))
- Each pilot is **isolated**
- Google Drive is used for:
  - storage
  - client interaction
  - audit trail
- Local project is used for:
  - processing
  - execution of CRC logic

---

## 8. Folder Structure Summary

### Local Project


data/clients/{CLIENT}/{PILOT}/
├── raw/
├── config/
│ └── column_mapping.yaml
├── processed/
├── outputs/
└── logs/


### Google Drive


{CLIENT}/
├── 01_INBOUND_RAW/{PILOT}/
├── 02_WORKING_PROCESSED/{PILOT}/
└── 03_OUTPUT_REPORTS/{PILOT}/


---

## 9. Standard Workflow

1. Receive or upload client data to Google Drive (`01_INBOUND_RAW`)
2. Copy data into local `raw/` folder
3. Configure or update `column_mapping.yaml`
4. Run ingestion process
5. Review outputs in `processed/`
6. Run CRC modules
7. Generate reports in `outputs/`
8. Upload final reports to Google Drive (`03_OUTPUT_REPORTS`)

---

## 10. Notes

- This process is designed to be:
  - simple
  - manual
  - repeatable
- No system integrations are required (file-based only)
- Suitable for pilot phase and early-stage operations