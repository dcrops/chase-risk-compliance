# Ingestion Mapping & Date Contract (v1)

Authoritative description of `column_mapping.yaml`: the schema ingestion accepts,
how dates are parsed, and how failures are reported.

Applies to:

- `data/clients/{CLIENT}/{PILOT}/config/column_mapping.yaml`
- `templates/column_mapping_template.yaml`
- `templates/examples/adp_column_mapping_example.yaml`

Implemented by `src/common/mapping_contract.py` and `src/common/date_parsing.py`,
consumed by `src/ingestion/ingest.py`.

---

## 1. Mapping schema

```yaml
# Optional: run-wide date format, applied to every dataset that does not
# override it. Defaults to ISO (%Y-%m-%d) when omitted.
date_format: "%d/%m/%Y"

<dataset>:
  source_file: <file name inside the pilot's raw/ directory>
  date_format: <optional, overrides the run-wide format for this dataset>
  date_formats:                 # optional, per canonical column
    <canonical date column>: <format or list of formats>
  rename:
    <source column>: <canonical column>
```

### Mapping direction

**Source column on the left, canonical column on the right.**

```yaml
rename:
  HireDt: start_date          # correct
```

The rename block is passed straight to `DataFrame.rename(columns=...)`, so the
left-hand side must match the header in the source CSV exactly, including
spaces and capitalisation. Declare `rename` even when the source headers are
already canonical.

### Required datasets

Ingestion cannot build the canonical model without all four:

| Dataset | Canonical output |
|---|---|
| `employees` | `processed/employees.csv` |
| `terminations` | `processed/terminations.csv` |
| `pay_events` | `processed/pay_events.csv`, `processed/payroll_transactions.csv` |
| `leave_ledger` | `processed/leave_ledger.csv` |

### Optional datasets

| Dataset | Canonical output |
|---|---|
| `leave_snapshot` | `processed/balances_snapshot.csv` |

`leave_snapshot` is skipped when absent. Any other top-level key is rejected, so
a typo in a dataset name fails rather than silently disabling a dataset.

### Canonical date columns

| Dataset | Canonical date column | Required |
|---|---|---|
| `employees` | `start_date` | no |
| `employees` | `termination_date` | no — used by LSL service-year calculation; `end_date` is accepted as a legacy alias |
| `terminations` | `termination_date` | yes |
| `pay_events` | `pay_date` | yes |
| `leave_ledger` | `event_date` | yes |
| `leave_snapshot` | `as_of_date` | no — derived from the latest `pay_date` when the source supplies none |

### Evidence fields

| Dataset | Canonical field | Notes |
|---|---|---|
| `terminations` | `evidence_reference` | Preferred by TERM-005 and Cross-Module evidence checks. Legacy aliases `evidence_ref`, `termination_evidence` and `document_id` remain intentional fallbacks via `src/common/evidence_fields.py`. |

---

## 2. Complete example

```yaml
# Vendor exports are day-first, except the leave extract.
date_format: "%d/%m/%Y"

employees:
  source_file: WORKER_MASTER.csv
  rename:
    Payroll No: employee_id
    Commencement Dt: start_date
    Engagement Basis: employment_type
    Std Hrs: standard_hours
    FTE Ratio: fte
    Hourly Rate: base_rate
    Cost Centre: department

terminations:
  source_file: TERM_REGISTER.csv
  rename:
    Payroll No: employee_id
    Separation Dt: termination_date
    Separation Category: termination_type
    Separation Notes: termination_reason
    Evidence Doc: evidence_reference

pay_events:
  source_file: PAYRUN_DETAIL.csv
  rename:
    Payroll No: employee_id
    Payment Dt: pay_date
    Pay Run Ref: pay_run_id
    Gross Earnings: gross_amount
    Ordinary Time Earnings: ote_amount
    Employer Super: super_amount
    Final Pay Flag: is_final_pay
    Earnings Code: pay_code

leave_ledger:
  # This extract comes from a reporting layer that emits ISO dates.
  source_file: LEAVE_TXNS.csv
  date_format: "%Y-%m-%d"
  rename:
    Txn Ref: transaction_id
    Payroll No: employee_id
    Effective Dt: event_date
    Leave Category: leave_type
    Movement Type: transaction_type
    Hours: units

leave_snapshot:
  source_file: LEAVE_BALANCES.csv
  rename:
    Payroll No: employee_id
    Leave Category: leave_type
    Balance Dt: as_of_date
    Balance Hours: balance
```

A worked non-canonical example ships at
`templates/examples/adp_column_mapping_example.yaml`, exercised end to end by
`tests/ingestion/test_ingest_adp_mapping.py`.

---

## 3. Date handling

### Explicit-format policy

Business dates are parsed **only** against declared formats. Pandas format
inference is not used, because it resolves ambiguous Australian dates
month-first and can null out valid ISO values when a column mixes formats.

`01/02/2024` under `%d/%m/%Y` is **1 February 2024**, not 2 January.

### Format resolution

Most specific declaration wins:

1. `<dataset>.date_formats.<canonical column>`
2. `<dataset>.date_format`
3. top-level `date_format`
4. default `%Y-%m-%d`

The default preserves existing behaviour: every committed pilot extract supplies
ISO dates, so mappings that declare nothing keep working.

### Supported formats

Any `strptime` format string, for example `%d/%m/%Y`, `%Y-%m-%d`, `%d-%m-%Y`,
`%d %b %Y`. A value without a `%` directive is rejected as a configuration
error.

### Mixed formats

Supported only where declared. Give a list and each value is tried in order:

```yaml
pay_events:
  source_file: PAYRUN_DETAIL.csv
  date_formats:
    pay_date:
      - "%d/%m/%Y"
      - "%Y-%m-%d"
```

Order matters for genuinely ambiguous values. An undeclared second format is an
error, not a silent fallback.

### Nulls

Blank, whitespace-only and missing values stay null. Where the canonical model
permits a null date (`employees.start_date`, `leave_snapshot.as_of_date`) that is
accepted. Where the canonical model requires the column, a column with no
parseable value at all fails.

### Canonical output

Parsed dates are written as `%Y-%m-%d` strings. Unchanged from previous
behaviour, so downstream modules and committed reference outputs are unaffected.

### Failure behaviour

Any non-null value that matches none of the declared formats raises
`DateParsingError` and stops ingestion. Values are never coerced to null.

```
employees: 4 of 4 non-null value(s) in column 'start_date' do not match the
declared date format(s) ['%Y-%m-%d']. Offending values: '01/02/2024',
'02/03/2024', '15/07/2023', '31/12/2023'. Declare the correct format for
employees.start_date in the column mapping, or correct the source data.
```

The message names the dataset, the column, the declared formats, how many values
failed, and up to five representative offending values.

---

## 4. Validation

`validate_mapping` runs before any dataset is read, so a bad mapping fails
immediately rather than part way through a run. All problems are reported
together so a client mapping can be corrected in one pass.

Normal `load_mapping` calls also verify that every `source_file` exists under
the pilot's `raw/` directory. Schema-only tooling may explicitly call
`load_mapping(..., check_source_files=False)`; ingestion never disables this
check.

Detected:

- missing or non-string `source_file`
- `source_file` that does not exist in the pilot's `raw/` directory
- missing, empty, or non-mapping `rename`
- two source columns mapped onto the same canonical column
- a required dataset that is not declared
- unknown top-level keys and unknown dataset keys
- the withdrawn `source` / `columns` template shape
- malformed date-format declarations, including a `date_formats` entry naming a
  column that is not a canonical date column for that dataset

Example:

```
config/column_mapping.yaml does not satisfy the ingestion contract:
  - terminations: required dataset is not declared in the mapping.
  - leave_ledger: required dataset is not declared in the mapping.
  - employees: uses the withdrawn template keys ['source', 'columns']. ...
  - pay_events: 'rename' is missing. Declare it as
    '<source column>: <canonical column>' even when the source headers are
    already canonical.
```

---

## 5. Migration note: the withdrawn template shape

Earlier templates documented a shape ingestion never read:

```yaml
# WITHDRAWN - rejected by validation
employees:
  source: WORKER_MASTER.csv
  columns:
    employee_id: Payroll No        # canonical on the left
```

It is **not** accepted, because the direction is reversed relative to the code:
silently accepting it would map canonical names onto vendor names and produce a
dataset with no canonical columns. No committed pilot mapping used it, so there
is no compatibility requirement and no deprecation shim.

To migrate:

1. `source` becomes `source_file`.
2. `columns` becomes `rename`.
3. **Swap each pair** so the source column is on the left.
4. Add `date_format` if the extract is not ISO.

```yaml
employees:
  source_file: WORKER_MASTER.csv
  rename:
    Payroll No: employee_id
```

`data/clients/CLT_KAGGLE_TEST/PILOT_001_2026_03_26/config/column_mapping.yaml`
predates the current canonical model (it declares a `leave_balances` dataset that
no longer exists) and is retained only as a historical artifact. It does not
satisfy this contract and is not re-runnable; see
`tests/common/test_mapping_contract.py`.

---

## 6. Related

- `docs/operations/client_intake_process.md` — where mappings sit in intake
- `docs/contracts/finding_identity_contract.md` — deterministic finding IDs
- `docs/operations/run_provenance.md` — run manifest
- `docs/contracts/termination_final_pay_contract.md` — TERM parses the canonical
  ISO dates this contract produces; the formats it lists apply to its own
  defensive re-parsing, not to ingestion
