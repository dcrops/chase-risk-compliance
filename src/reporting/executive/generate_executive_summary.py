from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from reporting.core.narrative_guard import (
    NarrativeMetrics,
    build_severity_interpretation,
    build_severity_distribution_line,
    build_classification_interpretation,
    build_recommendation_summary,
    build_calibrated_risk_line,
    build_calibrated_module_focus_line,
    ensure_valid_narrative,
    ensure_valid_report_text,
)


def load_summary(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing summary file: {path}")
    return pd.read_csv(path)


def derive_signals(df: pd.DataFrame) -> dict:
    total_findings = int(df["finding_count"].sum())

    class_summary = (
        df.groupby("classification")["finding_count"]
        .sum()
        .to_dict()
    )

    severity_summary = (
        df.groupby("severity")["finding_count"]
        .sum()
        .to_dict()
    )

    high_df = df[df["severity"] == "HIGH"]

    high_by_module = (
        high_df.groupby("module")["finding_count"]
        .sum()
        .sort_values(ascending=False)
    )

    top_high_modules = high_by_module.head(2).index.tolist()

    class_shares = {
        k: (v / total_findings) if total_findings else 0
        for k, v in class_summary.items()
    }

    dominant_classification = (
        max(class_summary, key=class_summary.get)
        if class_summary else "UNKNOWN"
    )
    dominant_severity = (
        max(severity_summary, key=severity_summary.get)
        if severity_summary else "UNKNOWN"
    )

    return {
        "total_findings": total_findings,
        "class_summary": class_summary,
        "severity_summary": severity_summary,
        "class_shares": class_shares,
        "dominant_classification": dominant_classification,
        "dominant_severity": dominant_severity,
        "top_high_modules": top_high_modules,
    }


def build_metrics(signals: dict) -> NarrativeMetrics:
    class_summary = signals.get("class_summary", {}) or {}
    severity_summary = signals.get("severity_summary", {}) or {}

    return NarrativeMetrics(
        total=int(signals.get("total_findings", 0) or 0),
        high=int(severity_summary.get("HIGH", 0) or 0),
        medium=int(severity_summary.get("MEDIUM", 0) or 0),
        low=int(severity_summary.get("LOW", 0) or 0),
        structural=int(class_summary.get("STRUCTURAL", 0) or 0),
        logical=int(class_summary.get("LOGICAL", 0) or 0),
        contextual=int(class_summary.get("CONTEXTUAL", 0) or 0),
        coverage="full",
    )


def build_module_focus_line(signals: dict, metrics: NarrativeMetrics) -> str:
    top_modules = signals.get("top_high_modules", []) or []

    narrative_labels = {
        "TERM": "termination handling",
        "RKEG": "record-keeping controls",
        "LEAVE": "leave calculation and balance integrity",
        "LSL": "long service leave eligibility and accrual",
        "CROSS_MODULE": "cross-module lifecycle consistency",
    }

    return build_calibrated_module_focus_line(
        top_modules=top_modules,
        module_labels=narrative_labels,
        m=metrics,
    )


def interpret_signals(signals: dict) -> dict:
    metrics = build_metrics(signals)

    severity_line = build_severity_interpretation(metrics)
    distribution_line = build_severity_distribution_line(metrics)
    classification_line = build_classification_interpretation(metrics)
    calibrated_risk_line = build_calibrated_risk_line(metrics)
    module_focus_line = build_module_focus_line(signals, metrics)

    summary_lines = [
        f"CRC identified {metrics.total} findings across the reviewed modules.",
        severity_line,
        distribution_line,
        classification_line,
        calibrated_risk_line,
        module_focus_line,
    ]

    what_this_means = (
        "This summary reflects the distribution of triggered findings in the supplied results. "
        "It is intended to describe the observed findings profile and does not, on its own, "
        "confirm payroll error, non-compliance, or quantified exposure."
    )

    recommended_focus = build_recommendation_summary(metrics)

    for line in summary_lines:
        ensure_valid_narrative(line, metrics)

    ensure_valid_narrative(recommended_focus, metrics)

    return {
        "summary_lines": summary_lines,
        "what_this_means": what_this_means,
        "recommended_focus": recommended_focus,
    }


def write_outputs(summary: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "executive_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)


def write_markdown(summary: dict, output_dir: Path) -> None:
    md_path = output_dir / "executive_summary.md"

    metrics = NarrativeMetrics(
        total=int(summary.get("total_findings", 0) or 0),
        high=int((summary.get("severity_summary") or {}).get("HIGH", 0) or 0),
        medium=int((summary.get("severity_summary") or {}).get("MEDIUM", 0) or 0),
        low=int((summary.get("severity_summary") or {}).get("LOW", 0) or 0),
        structural=int((summary.get("class_summary") or {}).get("STRUCTURAL", 0) or 0),
        logical=int((summary.get("class_summary") or {}).get("LOGICAL", 0) or 0),
        contextual=int((summary.get("class_summary") or {}).get("CONTEXTUAL", 0) or 0),
        coverage="full",
    )

    lines = ["## Executive Summary", ""]

    for line in summary["summary_lines"]:
        lines.append(f"- {line}")

    lines.append("")
    lines.append("### What this means")
    lines.append("")
    lines.append(summary["what_this_means"])

    lines.append("")
    lines.append("### Recommended focus")
    lines.append("")
    lines.append(summary["recommended_focus"])

    final_text = "\n".join(lines)
    ensure_valid_report_text(final_text, metrics)
    md_path.write_text(final_text, encoding="utf-8")


def run(summary_file: Path, output_dir: Path) -> None:
    df = load_summary(summary_file)

    signals = derive_signals(df)
    interpretation = interpret_signals(signals)

    final = {**signals, **interpretation}

    write_outputs(final, output_dir)
    write_markdown(final, output_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)

    args = parser.parse_args()

    run(
        summary_file=Path(args.input),
        output_dir=Path(args.output_dir),
    )