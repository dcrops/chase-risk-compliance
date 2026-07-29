# Chase Risk & Compliance (CRC)

System for analysing payroll and operational data to surface hidden risks and governance issues

---

## Problem

Payroll and operational systems are designed to process transactions, but they do not identify structural inconsistencies, configuration drift, or hidden risks that accumulate over time.

---

## Solution

CRC is a modular diagnostics system that ingests payroll data, applies rule-based analysis across multiple domains, and generates structured outputs highlighting potential risks and inconsistencies.

---

## Architecture

- Data ingestion and schema validation  
- Rule engine (YAML-driven, domain-based)  
- Multi-module analysis:
  - Leave (LEAVE)
  - Long Service Leave (LSL)
  - Termination (TERM)
  - Record Keeping & Evidence Gaps (RKEG)  
- Findings generation with structured evidence  
- Reporting layer (Markdown → HTML → PDF)  

---

## Running a pilot

```bash
# Ingest raw client extracts into the canonical model
python scripts/run_ingestion.py --client CLT_EXAMPLE --pilot PILOT_001

# Run the full diagnostic pipeline
python scripts/run_full_pipeline.py --client CLT_EXAMPLE --pilot PILOT_001

# Run the offline test suite
python -m pytest
```

Ingestion validates the pilot's `column_mapping.yaml` before reading any data,
parses dates only against declared formats, and writes a run manifest to
`outputs/run_manifest_ingestion.json`. Each diagnostic module writes its own
`outputs/run_manifest_{module}.json`.

### Documentation

| Document | Covers |
|---|---|
| [Ingestion mapping & date contract](docs/contracts/ingestion_mapping_contract.md) | Mapping schema and direction, required datasets, date formats, validation, migration |
| [Finding identity contract](docs/contracts/finding_identity_contract.md) | Deterministic finding IDs, required evidence, rerun stability |
| [Run provenance](docs/operations/run_provenance.md) | Run manifest contents and limitations |
| [Testing](docs/operations/testing.md) | Default offline suite, network tests, markers |
| [Client intake process](docs/operations/client_intake_process.md) | End-to-end pilot workflow |
| [Pilot readiness checklist](docs/operations/pilot_readiness_checklist.md) | Gating items and accepted limitations |
| [Changelog](CHANGELOG.md) | Notable changes |

---

## Key Features

- Deterministic rule-based detection of anomalies and inconsistencies  
- Modular design enabling domain-specific diagnostics  
- Structured findings with traceable evidence  
- Executive-ready reporting outputs for business stakeholders  

---

## AI Direction

A prototype internal RAG-based copilot has been developed to support rule exploration and reasoning.

Future development focuses on AI-assisted explanation and decision support layered on top of the rule-based system.

---

## Tech Stack

- Python  
- Pandas  
- YAML (rule configuration)  
- Markdown / HTML / PDF reporting  

---

## Why this project

CRC reflects my approach to engineering: starting from a real-world business problem, designing a system architecture, and building a working solution that produces meaningful, actionable outputs.
