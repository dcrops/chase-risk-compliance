# Payroll Diagnostics Engine

Developed as part of the Chase Risk & Compliance (CRC) platform.

A modular operational diagnostics and governance platform designed to analyse business datasets, identify risk indicators, surface evidence gaps, detect operational inconsistencies, and generate executive-ready reporting.

CRC was built as an end-to-end diagnostics system demonstrating how structured analytics, rule-based reasoning, and evidence-backed reporting can be combined to improve operational visibility and governance outcomes.

Although demonstrated using payroll datasets, the underlying architecture was intentionally designed to support broader operational diagnostics and governance use cases.

---

# Project Status

Version 1 engineering is complete. The engine has completed Architecture,
Verification, Enterprise Hardening, Acceptance, Rule Quality and Pilot Safety
reviews. Its deterministic architecture and public contracts are considered
stable for an owner-supervised pilot.

The current phase is **Pilot Validation & Rule Calibration**. Controlled client
pilots will be used to measure false positives, possible false negatives,
investigation effort, report clarity and payroll specialist usefulness.

Future rule changes will be evidence-driven:

> Validate with real payroll data first. Calibrate second.

Architectural change is not a current objective. Engineering defects will still
be corrected when reproduced, but threshold, severity, scope and wording
changes require pilot evidence and follow the documented calibration process.

See the [roadmap](docs/ROADMAP.md) and
[pilot validation strategy](docs/operations/pilot_validation_strategy.md).

---

# Platform Highlights

* 5 diagnostic domains
* Modular rule-based architecture
* Data ingestion and validation pipelines
* Evidence-backed findings generation
* Severity classification framework
* Executive reporting suite
* PDF and HTML report generation
* Client-isolated review architecture
* Governance-focused reporting outputs

---

# The Problem

Most operational systems are designed to process transactions and generate reports.

They are generally not designed to proactively identify:

* Hidden operational risks
* Data quality issues
* Process inconsistencies
* Evidence gaps
* Governance weaknesses
* Cross-system integrity failures
* Emerging risk patterns

As a result, issues often remain undetected until audits, investigations, employee disputes, acquisitions, or regulatory reviews occur.

---

# The Solution

CRC acts as an independent diagnostics layer that sits above operational datasets.

The platform ingests structured data, applies domain-specific rule analysis, generates evidence-backed findings, and produces executive-ready outputs that support operational review and governance activities.

The platform focuses on:

* Risk detection
* Operational assurance
* Data quality assessment
* Governance visibility
* Explainable findings
* Evidence traceability
* Executive reporting

Rather than replacing operational systems, CRC provides an additional layer of analytical review designed to identify issues that may otherwise remain hidden.

---

# Example Outputs

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
| [Roadmap](docs/ROADMAP.md) | Completed engineering phases and current pilot validation phase |
| [Version 1 engineering status](docs/engineering_status.md) | Stable contracts and change posture during pilot validation |
| [Ingestion mapping & date contract](docs/contracts/ingestion_mapping_contract.md) | Mapping schema and direction, required datasets, date formats, validation, migration |
| [Finding identity contract](docs/contracts/finding_identity_contract.md) | Deterministic finding IDs, required evidence, rerun stability |
| [Termination / final pay contract](docs/contracts/termination_final_pay_contract.md) | Final-pay identification, evidence fields, lifecycle interpretation for pilots |
| [Pilot validation strategy](docs/operations/pilot_validation_strategy.md) | Pilot safeguards, evidence collection, measures and success criteria |
| [Rule calibration process](docs/rules/calibration_process.md) | Evidence requirements and approval gates for future rule changes |
| [Technical debt register](docs/operations/technical_debt_register.md) | Classified deferred work and pilot mitigations |
| [Run provenance](docs/operations/run_provenance.md) | Run manifest contents and limitations |
| [Testing](docs/operations/testing.md) | Default offline suite, network tests, markers |
| [Client intake process](docs/operations/client_intake_process.md) | End-to-end pilot workflow |
| [Pilot readiness checklist](docs/operations/pilot_readiness_checklist.md) | Gating items and accepted limitations |
| [Changelog](CHANGELOG.md) | Notable changes |

Map termination evidence to the canonical `evidence_reference` field. Legacy
aliases are still accepted by evidence-dependent rules, but only as intentional
fallbacks. LSL service years use `termination_date` (with `end_date` as a legacy
alias) so terminated employees do not keep accruing to the snapshot date.

Finding counts are counts of triggered checks. The executive pack includes a
lifecycle concentration section so that overlapping TERM / LEAVE / RKEG /
Cross-Module findings for the same employee are read in context.

---

## Key Features


## Executive Summary

The platform generates executive-ready reporting designed to provide rapid visibility of key risk areas, severity distribution, and recommended review priorities.

![Executive Summary](docs/images/executive-summary.png)

---

## Module Risk Analysis

CRC analyses multiple governance domains independently and provides risk summaries for each module.

![Module Summary Overview](docs/images/module-summary-overview.png)

---

# System Architecture

The architecture below illustrates the end-to-end diagnostics workflow from ingestion through to executive reporting.

```mermaid
flowchart TD

    A[Operational Data Sources] --> B[Data Ingestion]

    B --> C[Data Validation]

    C --> D[Rule-Based Diagnostic Engine]

    D --> E1[Leave & Entitlement Leakage]
    D --> E2[Long Service Leave]
    D --> E3[Termination Exposure]
    D --> E4[Record Keeping & Evidence Gaps]
    D --> E5[Cross Module Integrity]

    E1 --> F[Evidence-Backed Risk Findings]
    E2 --> F
    E3 --> F
    E4 --> F
    E5 --> F

    F --> G[Severity Classification]

    G --> H[Executive Reporting]

    H --> I1[Executive Summary]
    H --> I2[Risk Profile]
    H --> I3[Detailed Findings]
    H --> I4[PDF & HTML Outputs]
```

---

## Sample Executive Report

A sample executive report generated by the platform is included in this repository.

[View Sample Executive Report](docs/sample_reports/crc_executive_pack.pdf)

---

# Getting Started

## Clone Repository

```bash
git clone https://github.com/dcrops/chase-risk-compliance.git
cd chase-risk-compliance
```

## Create Virtual Environment

```bash
python -m venv .venv
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Execute a Review

Run one of the example pilot reviews contained within the repository to generate findings and executive reports.

Review workspaces are located under:

```text
data/clients/
```

---

# Architecture Overview

CRC follows a layered architecture:

1. Data Ingestion
2. Data Validation
3. Diagnostic Analysis
4. Findings Generation
5. Executive Reporting

Each layer has a clearly defined responsibility, allowing the platform to remain modular, maintainable, and extensible.

Diagnostic runs are organised into isolated client review workspaces containing inputs, findings, outputs, and executive reports.

---

# Diagnostic Domains

## Leave & Entitlement Leakage (LEAVE)

Analyses leave balances, leave transactions, entitlement calculations, and reconciliation issues.

## Long Service Leave (LSL)

Reviews long service leave activity, exposure, balance integrity, and accrual-related risks.

## Termination Exposure (TERM)

Identifies termination-related evidence gaps, final pay risks, lifecycle inconsistencies, and process weaknesses.

## Record Keeping & Evidence Gaps (RKEG)

Evaluates supporting documentation, audit evidence, and governance controls.

## Cross-Module Integrity

Detects inconsistencies across related datasets and linked operational processes.

---

# Key Features

## Data Ingestion & Validation

* CSV-based ingestion framework
* Schema validation
* Coverage analysis
* Data quality assessment
* Missing field detection
* Readiness scoring

## Modular Rule Engine

* Configuration-driven diagnostics
* Domain-specific rule libraries
* Independent module execution
* Extensible architecture

## Findings Generation

* Evidence-backed findings
* Severity classification
* Traceable outputs
* Structured risk reporting

## Executive Reporting

* Executive summaries
* Risk profile reporting
* Detailed findings reports
* HTML outputs
* PDF outputs

---

# Key Engineering Concepts

CRC demonstrates several software engineering and analytics engineering patterns:

* Layered system architecture
* Modular rule engine design
* Configuration-driven diagnostics
* Data quality validation workflows
* Evidence-backed decision support
* Severity classification frameworks
* Cross-domain integrity analysis
* Executive reporting pipelines
* Reusable reporting components
* Client-isolated review workspaces

The project was intentionally structured to separate ingestion, validation, diagnostics, findings generation, and reporting into independently maintainable layers.

---

# Engineering Challenges Solved

This project demonstrates practical solutions for:

* Modular diagnostics architecture
* Rule-based analytical systems
* Explainable findings generation
* Structured evidence handling
* Governance-focused reporting
* Cross-domain integrity validation
* Operational intelligence workflows
* Executive-level communication

---

# Repository Structure

```text
src/
├── ingestion/
├── validation/
├── diagnostics/
├── findings/
├── reporting/
└── shared/

data/
└── clients/
    └── <client_name>/
        └── <review_name>/
            ├── inputs/
            ├── findings/
            ├── outputs/
            └── reports/

docs/
├── images/
└── sample_reports/

scripts/
templates/
tests/
```

---

# Client Review Structure

CRC is designed around isolated client review workspaces.

Each review contains its own:

* Input datasets
* Diagnostic findings
* Generated outputs
* Executive reports

This structure supports repeatable analysis, auditability, and separation of review artefacts.

---

# Technology Stack

## Core Technologies

* Python
* Pandas
* YAML

## Data Processing

* CSV ingestion pipelines
* Data validation frameworks
* Rule-based analytics

## Reporting

* Markdown generation
* HTML rendering
* PDF generation
* Executive reporting

## Engineering Practices

* Modular architecture
* Configuration-driven rules
* Evidence traceability
* Layered system design

## Testing & Tooling

* PyTest
* Git
* GitHub

---

# Public Repository Notice

This repository is a public-safe version of the Payroll Diagnostics Engine intended to demonstrate architecture, engineering approach, diagnostics workflows, and reporting capabilities.

Some domain-specific rule logic, thresholds, datasets, and implementation details have been simplified or removed.

No client data is included.

All datasets used within this repository are synthetic or demonstration-only.

---

# Portfolio

Portfolio Website:

https://journey.chaseriskandcompliance.com.au/

GitHub:

https://github.com/dcrops

---

# Why This Project

CRC reflects my approach to engineering:

* Start with a real-world business problem
* Design modular architectures
* Build explainable systems
* Focus on operational outcomes
* Produce actionable outputs
* Balance engineering with governance considerations

The project demonstrates software engineering, analytics engineering, operational intelligence, diagnostics, reporting, and governance-aware system design concepts that later informed the development of AI-powered operational intelligence platforms.
