from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable
from datetime import date

from reporting.core.cover_page import build_cover_page
from reporting.core.narrative_guard import (
    NarrativeMetrics,
    build_severity_interpretation,
    build_severity_distribution_line,
    build_classification_interpretation,
    build_coverage_statement,
    build_recommendation_summary,
    ensure_valid_narrative,
    ensure_valid_report_text,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "clients"

MODULE_FINDINGS = {
    "TERM": "term_findings.csv",
    "RKEG": "rkeg_findings.csv",
    "LEAVE": "leave_leakage_findings.csv",
    "LSL": "lsl_findings.csv",
    "CROSS_MODULE": "cross_module_findings.csv",
}


def _format_date_range_human(raw_range: str) -> str:
    if not raw_range or " to " not in raw_range:
        return raw_range

    start_raw, end_raw = [x.strip() for x in raw_range.split(" to ", 1)]

    try:
        start = date.fromisoformat(start_raw)
        end = date.fromisoformat(end_raw)
    except ValueError:
        return raw_range

    if start == end:
        return start.strftime("%d %b %Y")

    return f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"


def run_cmd(cmd: list[str]) -> None:
    print("\n[RUN]", " ".join(cmd))
    subprocess.run(cmd, check=True)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def outputs_dir_for(client: str, pilot: str) -> Path:
    return DATA_ROOT / client / pilot / "outputs"


def build_review_period(outputs_dir: Path) -> str:
    candidates = [
        outputs_dir / "leave_data_window.csv",
        outputs_dir / "lsl_data_window.csv",
        outputs_dir / "rkeg_data_window.csv",
        outputs_dir / "cross_module_data_window.csv",
    ]
    for path in candidates:
        rows = load_csv_rows(path)
        if not rows:
            continue
        row = rows[0]
        start_raw = (row.get("first_date") or row.get("start_date") or "").strip()
        end_raw = (row.get("last_date") or row.get("end_date") or "").strip()
        if start_raw and end_raw:
            return f"{start_raw} to {end_raw}"
    return "Review period not clearly identifiable from supplied data"


def load_all_findings(outputs_dir: Path) -> list[dict[str, str]]:
    all_rows: list[dict[str, str]] = []
    for module, filename in MODULE_FINDINGS.items():
        rows = load_csv_rows(outputs_dir / filename)
        for row in rows:
            row = dict(row)
            row["module"] = module
            all_rows.append(row)
    return all_rows


def severity_counts(findings: Iterable[dict[str, str]]) -> dict[str, int]:
    counter = Counter((r.get("severity") or "").upper() for r in findings)
    return {
        "HIGH": counter.get("HIGH", 0),
        "MEDIUM": counter.get("MEDIUM", 0),
        "LOW": counter.get("LOW", 0),
    }


def classification_counts(findings: Iterable[dict[str, str]]) -> dict[str, int]:
    counter = Counter((r.get("classification") or "").upper() for r in findings)
    return {
        "STRUCTURAL": counter.get("STRUCTURAL", 0),
        "LOGICAL": counter.get("LOGICAL", 0),
        "CONTEXTUAL": counter.get("CONTEXTUAL", 0),
    }


def pick_sample_findings(findings: list[dict[str, str]], max_items: int = 3) -> list[dict[str, str]]:
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    preferred_modules = ["TERM", "LEAVE", "RKEG", "CROSS_MODULE", "LSL"]

    cleaned = []
    for row in findings:
        cleaned.append(
            {
                "module": row.get("module", ""),
                "rule_code": row.get("rule_code", ""),
                "severity": (row.get("severity") or "").upper(),
                "employee_id": row.get("employee_id", ""),
                "message": row.get("message") or row.get("description") or "No description provided.",
                "next_action": row.get("next_action") or "",
            }
        )

    cleaned.sort(
        key=lambda r: (
            severity_rank.get(r["severity"], 99),
            preferred_modules.index(r["module"]) if r["module"] in preferred_modules else 99,
            r["rule_code"],
        )
    )

    selected: list[dict[str, str]] = []
    used_modules: set[str] = set()

    for row in cleaned:
        if row["module"] not in used_modules:
            selected.append(row)
            used_modules.add(row["module"])
        if len(selected) >= max_items:
            return selected

    return cleaned[:max_items]


def module_label(module: str) -> str:
    return {
        "TERM": "Termination processing",
        "LEAVE": "Leave and entitlement integrity",
        "RKEG": "Record-keeping and evidence",
        "LSL": "Long service leave",
        "CROSS_MODULE": "Cross-module integrity",
    }.get(module, module)


def comparison_summary_text(full_outputs_dir: Path) -> str | None:
    insight_path = full_outputs_dir / "crc_coverage_insight.md"
    if not insight_path.exists():
        return None
    return insight_path.read_text(encoding="utf-8").strip()


def write_pilot_report(
    client: str,
    pilot: str,
    organisation_name: str,
    outputs_dir: Path,
    findings: list[dict[str, str]],
    comparison_text: str | None = None,
) -> Path:
    report_path = outputs_dir / "pilot_report.md"

    total = len(findings)
    sev = severity_counts(findings)
    cls = classification_counts(findings)
    review_period = build_review_period(outputs_dir)
    display_review_period = _format_date_range_human(review_period)
    samples = pick_sample_findings(findings, max_items=3)

    metrics = NarrativeMetrics(
        total=total,
        high=sev["HIGH"],
        medium=sev["MEDIUM"],
        low=sev["LOW"],
        structural=cls["STRUCTURAL"],
        logical=cls["LOGICAL"],
        contextual=cls["CONTEXTUAL"],
        coverage="partial",  # pilot reviews should be framed as partial coverage
    )

    severity_interp = build_severity_interpretation(metrics)
    severity_dist = build_severity_distribution_line(metrics)
    classification_interp = build_classification_interpretation(metrics)
    coverage_interp = build_coverage_statement(metrics)
    recommendation_interp = build_recommendation_summary(metrics)

    for text in [
        severity_interp,
        severity_dist,
        classification_interp,
        coverage_interp,
        recommendation_interp,
    ]:
        ensure_valid_narrative(text, metrics)

    logo_path = (
        PROJECT_ROOT / "src" / "reporting" / "assets" / "crc_logo_full.png"
    ).as_uri()

    lines: list[str] = []

    lines.append(
        build_cover_page(
            report_title="Payroll Integrity Pilot Review",
            organisation_name=organisation_name,
            review_period=display_review_period,
            logo_path=logo_path,
            subtitle="Payroll Risk & Evidence Review",
            prepared_as_at=date.today().strftime("%d %b %Y"),
            confidentiality_label="Confidential",
        )
    )
    lines.append("")

    lines.append("# Payroll Integrity Pilot Review")
    lines.append("")
    lines.append(f"**Organisation:** {organisation_name}  ")
    lines.append(f"**Pilot:** {pilot}  ")
    lines.append(f"**Review Period:** {display_review_period}  ")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Executive Summary")
    lines.append("")
    lines.append(
        "A targeted payroll diagnostics review was conducted using available payroll data to identify triggered findings across key payroll integrity and evidence-related risk areas."
    )
    lines.append("")
    lines.append(f"**Total Findings Identified:** **{total}**")
    lines.append("")
    lines.append("### Severity Breakdown")
    lines.append("")
    lines.append(f"- High: {sev['HIGH']}")
    lines.append(f"- Medium: {sev['MEDIUM']}")
    lines.append(f"- Low: {sev['LOW']}")
    lines.append("")
    lines.append("### Interpretation")
    lines.append("")
    lines.append(severity_interp)
    lines.append("")
    lines.append(severity_dist)
    lines.append("")
    lines.append(classification_interp)
    lines.append("")
    lines.append(coverage_interp)
    lines.append("")
    lines.append("### Recommended Focus")
    lines.append("")
    lines.append(recommendation_interp)
    lines.append("")
    lines.append("## 2. Why This Matters")
    lines.append("")
    lines.append(
        "This pilot review is designed to surface triggered findings from the supplied payroll data so they can be validated and prioritised for follow-up."
    )
    lines.append("")
    lines.append("- Triggered findings may indicate process weaknesses, data inconsistencies, or evidentiary gaps")
    lines.append("- Higher-severity findings should be reviewed first to confirm root cause and operational impact")
    lines.append("- Lower-severity findings can still highlight control weaknesses worth addressing over time")
    lines.append("")
    lines.append(
        "This pilot is intended to provide an initial evidence-based view of observed issues within the supplied data, not a full assurance conclusion."
    )
    lines.append("")
    lines.append("## 3. Sample Findings")
    lines.append("")
    lines.append("*This pilot includes a limited selection of findings to demonstrate the types of issues identified.*")
    lines.append("")

    for idx, row in enumerate(samples, start=1):
        lines.append(f"### Finding {idx} — {module_label(row['module'])}")
        lines.append("")
        lines.append(f"- **Rule:** {row['rule_code']}")
        lines.append(f"- **Severity:** {row['severity']}")
        if row["employee_id"]:
            lines.append(f"- **Example employee:** {row['employee_id']}")
        lines.append("")
        lines.append("**Issue**")
        lines.append(row["message"])
        lines.append("")
        lines.append("**Suggested Action**")
        lines.append(
            row["next_action"]
            or "Review the relevant process and confirm alignment with expected payroll and employee lifecycle controls."
        )
        lines.append("")

    lines.append(
        "These examples represent a subset of the findings identified and are intended to illustrate the types of triggered conditions present rather than the full extent of issues across the review."
    )
    lines.append("")

    lines.append("## 4. Scope & Methodology")
    lines.append("")
    lines.append("This review was conducted using structured payroll data extracts and rule-based diagnostics.")
    lines.append("")
    lines.append("- No system access was required")
    lines.append("- Analysis focused on payroll transactions and derived outcomes")
    lines.append("- Findings reflect triggered rule conditions observable within the supplied data")
    lines.append("- All findings are derived directly from supplied payroll data and system outputs")
    lines.append("")

    if comparison_text:
        lines.append("## 5. Optional Coverage Insight")
        lines.append("")
        lines.append(comparison_text)
        lines.append("")
        lines.append("## 6. Next Steps")
        lines.append("")
    else:
        lines.append("## 5. Next Steps")
        lines.append("")

    lines.append("A full review can provide:")
    lines.append("")
    lines.append("- complete findings across all modules")
    lines.append("- detailed employee-level impact analysis")
    lines.append("- root cause identification")
    lines.append("- practical remediation guidance")
    lines.append("- audit-ready reporting outputs")
    lines.append("")

    final_text = "\n".join(lines)
    ensure_valid_report_text(final_text, metrics)
    report_path.write_text(final_text, encoding="utf-8")

    print(f"[OK] Wrote pilot report: {report_path}")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a CRC pilot and generate a client-facing pilot report.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--pilot", required=True)
    parser.add_argument("--mode", required=True, choices=["payroll_only", "full"])
    parser.add_argument("--include-supporting", action="store_true")
    parser.add_argument("--organisation-name", default="Organisation not specified")
    parser.add_argument("--comparison-full-pilot", help="Optional full-data pilot used for comparison insight.")
    args = parser.parse_args()

    outputs_dir = outputs_dir_for(args.client, args.pilot)

    pipeline_cmd = [
        sys.executable,
        str(PROJECT_ROOT / "scripts" / "run_full_pipeline.py"),
        "--client",
        args.client,
        "--pilot",
        args.pilot,
        "--mode",
        args.mode,
    ]
    if args.include_supporting:
        pipeline_cmd.append("--include-supporting")
    run_cmd(pipeline_cmd)

    run_cmd(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "run_cross_module_summary.py"),
            "--client",
            args.client,
            "--pilot",
            args.pilot,
        ]
    )

    run_cmd(
        [
            sys.executable,
            "-m",
            "reporting.executive.generate_executive_summary",
            "--input",
            str(outputs_dir / "crc_summary_module_x_classification_x_severity.csv"),
            "--output-dir",
            str(outputs_dir / "executive"),
        ]
    )

    comparison_text = None

    if args.comparison_full_pilot:
        full_outputs = outputs_dir_for(args.client, args.comparison_full_pilot)

        run_cmd(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_coverage_summary.py"),
                "--client",
                args.client,
                "--pilot",
                args.pilot,
            ]
        )

        run_cmd(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_coverage_summary.py"),
                "--client",
                args.client,
                "--pilot",
                args.comparison_full_pilot,
            ]
        )

        run_cmd(
            [
                sys.executable,
                "-m",
                "scripts.run_coverage_comparison",
                "--client",
                args.client,
                "--payroll-pilot",
                args.pilot,
                "--full-pilot",
                args.comparison_full_pilot,
            ]
        )

        run_cmd(
            [
                sys.executable,
                "-m",
                "scripts.run_coverage_insight",
                "--client",
                args.client,
                "--full-pilot",
                args.comparison_full_pilot,
            ]
        )

        comparison_text = comparison_summary_text(full_outputs)

    findings = load_all_findings(outputs_dir)
    write_pilot_report(
        client=args.client,
        pilot=args.pilot,
        organisation_name=args.organisation_name,
        outputs_dir=outputs_dir,
        findings=findings,
        comparison_text=comparison_text,
    )

    run_cmd(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "render_pilot_report.py"),
            "--client",
            args.client,
            "--pilot",
            args.pilot,
        ]
    )


if __name__ == "__main__":
    main()