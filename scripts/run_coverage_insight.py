from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "data" / "clients"


def _pct_change(base: int, new: int) -> str:
    if base == 0:
        return "n/a"
    change = ((new - base) / base) * 100
    return f"{int(round(change))}%"


def _module_dependency_statement(module: str, payroll_total: int, full_total: int, delta: int) -> str:
    if delta == 0:
        if module == "CROSS_MODULE":
            return (
                "- No additional findings were identified with broader datasets. "
                "Based on this comparison run, this module was assessable from payroll-only data."
            )
        return (
            "- No additional findings were identified with broader datasets. "
            "Based on this comparison run, this module did not show expanded finding coverage when broader data was included."
        )

    pct = _pct_change(payroll_total, full_total)

    if module == "TERM":
        return (
            f"- Additional findings identified: {delta} ({pct} increase)\n"
            "- In this comparison, broader datasets identified additional termination-related findings "
            "that were not triggered in the payroll-only run."
        )

    if module == "RKEG":
        return (
            f"- Additional findings identified: {delta} ({pct} increase)\n"
            "- In this comparison, broader datasets identified additional record-keeping and evidence-related findings "
            "that were not triggered in the payroll-only run."
        )

    if module == "LSL":
        return (
            f"- Additional findings identified: {delta} ({pct} increase)\n"
            "- In this comparison, broader datasets identified additional long service leave-related findings "
            "that were not triggered in the payroll-only run."
        )

    if module == "LEAVE":
        return (
            f"- Additional findings identified: {delta} ({pct} increase)\n"
            "- In this comparison, broader datasets identified additional leave-related findings "
            "that were not triggered in the payroll-only run."
        )

    if module == "CROSS_MODULE":
        return (
            f"- Additional findings identified: {delta} ({pct} increase)\n"
            "- In this comparison, broader datasets identified additional cross-module findings "
            "that were not triggered in the payroll-only run."
        )

    return f"- Additional findings identified: {delta} ({pct} increase)"


def build_insight(client: str, full_pilot: str) -> None:
    outputs_dir = DATA_ROOT / client / full_pilot / "outputs"
    comparison_path = outputs_dir / "crc_coverage_comparison.csv"

    if not comparison_path.exists():
        raise FileNotFoundError(f"Missing comparison file: {comparison_path}")

    df = pd.read_csv(comparison_path)

    module_order = ["LEAVE", "LSL", "TERM", "RKEG", "CROSS_MODULE"]

    df["module"] = df["module"].astype(str).str.strip().str.upper()

    ordered_rows = []
    for module in module_order:
        match = df[df["module"] == module]
        if not match.empty:
            ordered_rows.append(match)

    if ordered_rows:
        df = pd.concat(ordered_rows, ignore_index=True)

    print("DEBUG module order:", df["module"].tolist())

    lines: list[str] = []
    lines.append("# CRC Coverage Insight")
    lines.append("")

    total_payroll = int(df["payroll_total"].sum())
    total_full = int(df["full_total"].sum())
    total_delta = int(total_full - total_payroll)
    total_delta_pct = _pct_change(total_payroll, total_full)

    lines.append("## Overview")
    lines.append("")
    lines.append(f"- Payroll-only findings: **{total_payroll}**")
    lines.append(f"- Full analysis findings: **{total_full}**")
    lines.append(
        f"- Additional findings identified with broader data coverage: **{total_delta} ({total_delta_pct})**"
    )
    lines.append("")

    if not df.empty:
        max_row = df.sort_values("delta_total", ascending=False).iloc[0]
        if int(max_row["delta_total"]) > 0:
            module = str(max_row["module"])
            uplift = _pct_change(int(max_row["payroll_total"]), int(max_row["full_total"]))
            lines.append(
                f"In this comparison, **{module}** had the largest increase in findings when broader datasets were included, "
                f"with **{int(max_row['delta_total'])} additional findings** ({uplift} increase)."
            )
            lines.append("")

    lines.append("## Module Breakdown")
    lines.append("")

    for _, row in df.iterrows():
        module = str(row["module"])

        payroll_total = int(row["payroll_total"])
        full_total = int(row["full_total"])
        delta = int(row["delta_total"])

        payroll_core = int(row["payroll_core"])
        payroll_supporting = int(row["payroll_supporting"])
        payroll_extended = int(row["payroll_extended"])

        full_core = int(row["full_core"])
        full_supporting = int(row["full_supporting"])
        full_extended = int(row["full_extended"])

        lines.append(f"### {module}")
        lines.append("")
        lines.append(
            f"- Payroll-only: {payroll_total} findings "
            f"(core={payroll_core}, supporting={payroll_supporting}, extended={payroll_extended})"
        )
        lines.append(
            f"- Full: {full_total} findings "
            f"(core={full_core}, supporting={full_supporting}, extended={full_extended})"
        )
        lines.append(_module_dependency_statement(module, payroll_total, full_total, delta))
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "This comparison shows how findings counts changed between the payroll-only run and the broader-data run."
    )
    lines.append("")
    lines.append(
        "Where additional findings appear in the broader-data run, this indicates that those findings were only triggered when additional datasets were available in that comparison."
    )
    lines.append("")
    lines.append(
        "Where no additional findings appear, this indicates that the broader-data run did not increase triggered findings for that module in this comparison."
    )
    lines.append("")
    lines.append(
        "These results should be interpreted as a comparison of triggered finding coverage between two analysis modes, not as a conclusion about overall payroll risk."
    )
    lines.append("")
    lines.append("This supports a tiered diagnostic approach:")
    lines.append("")
    lines.append("- Payroll-only → baseline review using core payroll datasets")
    lines.append("- Full analysis → broader review using additional available datasets")
    lines.append("")

    out_path = outputs_dir / "crc_coverage_insight.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote: {out_path}")
    print("\n--- Preview ---\n")
    print("\n".join(lines[:30]))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate CRC coverage insight markdown.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--full-pilot", required=True)
    args = parser.parse_args()

    build_insight(client=args.client, full_pilot=args.full_pilot)


if __name__ == "__main__":
    main()