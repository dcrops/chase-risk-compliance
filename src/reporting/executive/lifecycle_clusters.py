"""Lifecycle concentration reporting for the executive pack.

Several rules across TERM, LEAVE, LSL, RKEG and Cross-Module Integrity examine
the same underlying lifecycle event from different angles. One post-termination
pay run can therefore satisfy checks in three modules, and a reader who treats
the finding count as a count of distinct problems will overstate what the data
shows.

This module is presentation only. It reads the consolidated findings that the
modules have already written and reports how they concentrate by employee and
by lifecycle theme. It does not suppress, merge or re-identify any finding, and
rule execution is unaffected.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

CONSOLIDATED_FINDINGS_FILENAME = "crc_all_module_findings.csv"

# Themes group the rules that examine one lifecycle event. Each rule belongs to
# at most one theme so the counts stay additive. Rules absent from every theme
# are reported as "Other checks".
LIFECYCLE_THEMES: Tuple[Tuple[str, Tuple[str, ...]], ...] = (
    (
        "Payroll activity after termination",
        (
            "TERM-010",
            "TERM-015",
            "TERM-017",
            "RKEG-PAY-010",
            "RKEG-TERM-001",
            "CM-003",
            "CM-006",
            "CM-015",
        ),
    ),
    (
        "Leave activity after termination",
        (
            "LEAVE-007",
            "LEAVE-013",
            "LSL-015",
            "TERM-008",
            "CM-002",
            "CM-012",
        ),
    ),
    (
        "Leave balances remaining at termination",
        (
            "TERM-007",
            "TERM-009",
            "LSL-024",
            "CM-001",
            "CM-004",
            "CM-005",
            "CM-007",
            "CM-008",
            "CM-010",
            "CM-013",
            "CM-014",
            "CM-018",
        ),
    ),
    (
        "Final pay identification and timing",
        (
            "TERM-001",
            "TERM-002",
            "TERM-003",
            "TERM-006",
            "TERM-013",
            "TERM-016",
        ),
    ),
    (
        "Termination evidence and documentation",
        (
            "TERM-005",
            "CM-017",
        ),
    ),
    (
        "Lifecycle record structure and completeness",
        (
            "TERM-004",
            "TERM-011",
            "TERM-012",
            "TERM-014",
            "RKEG-EMP-004",
            "CM-011",
            "CM-016",
            "CM-019",
        ),
    ),
)

OTHER_THEME_LABEL = "Other checks"

# CM-020 is derived by counting other cross-module findings for the same
# employee. It is a cluster indicator, not an independent concern, so it is
# reported separately rather than inflating the concentration counts.
CLUSTER_INDICATOR_RULES: frozenset[str] = frozenset({"CM-020"})

_THEME_BY_RULE: Dict[str, str] = {
    rule_code: theme for theme, rule_codes in LIFECYCLE_THEMES for rule_code in rule_codes
}


def theme_for_rule(rule_code: str | None) -> str:
    return _THEME_BY_RULE.get((rule_code or "").strip().upper(), OTHER_THEME_LABEL)


@dataclass
class EmployeeCluster:
    employee_id: str
    finding_count: int
    high_count: int
    modules: List[str] = field(default_factory=list)
    themes: List[str] = field(default_factory=list)


@dataclass
class LifecycleConcentration:
    total_findings: int = 0
    counted_findings: int = 0
    cluster_indicator_findings: int = 0
    employee_count: int = 0
    unattributed_findings: int = 0
    employees: List[EmployeeCluster] = field(default_factory=list)
    theme_counts: List[Tuple[str, int]] = field(default_factory=list)

    @property
    def top_employee_share(self) -> float:
        if not self.counted_findings or not self.employees:
            return 0.0
        return self.employees[0].finding_count / self.counted_findings

    @property
    def findings_per_employee(self) -> float:
        if not self.employee_count:
            return 0.0
        return self.counted_findings / self.employee_count


def summarise_lifecycle_concentration(
    rows: Iterable[Mapping[str, str]],
) -> LifecycleConcentration:
    """Aggregate consolidated finding rows by employee and lifecycle theme."""
    summary = LifecycleConcentration()

    per_employee: Dict[str, EmployeeCluster] = {}
    theme_totals: Dict[str, int] = {}

    for row in rows:
        summary.total_findings += 1

        rule_code = (row.get("rule_code") or "").strip().upper()

        if rule_code in CLUSTER_INDICATOR_RULES:
            summary.cluster_indicator_findings += 1
            continue

        summary.counted_findings += 1

        theme = theme_for_rule(rule_code)
        theme_totals[theme] = theme_totals.get(theme, 0) + 1

        employee_id = (row.get("employee_id") or "").strip()
        if not employee_id:
            summary.unattributed_findings += 1
            continue

        cluster = per_employee.setdefault(
            employee_id, EmployeeCluster(employee_id=employee_id, finding_count=0, high_count=0)
        )
        cluster.finding_count += 1

        if (row.get("severity") or "").strip().upper() == "HIGH":
            cluster.high_count += 1

        module = (row.get("module") or "").strip().upper()
        if module and module not in cluster.modules:
            cluster.modules.append(module)

        if theme not in cluster.themes:
            cluster.themes.append(theme)

    summary.employee_count = len(per_employee)
    summary.employees = sorted(
        per_employee.values(),
        key=lambda c: (-c.finding_count, -c.high_count, c.employee_id),
    )
    summary.theme_counts = sorted(
        theme_totals.items(), key=lambda item: (-item[1], item[0])
    )

    return summary


def _fmt_pct(value: float) -> str:
    return f"{round(value * 100)}%"


def build_lifecycle_concentration_markdown(
    summary: LifecycleConcentration,
    top_employees: int = 5,
) -> str:
    lines: List[str] = []

    lines.append(
        "Findings are counts of triggered checks, not counts of distinct payroll events "
        "or confirmed errors. Several checks across different modules deliberately "
        "examine the same lifecycle event from different angles, so one termination, "
        "pay run or leave transaction can raise findings in more than one module. This "
        "section shows how the findings concentrate so that volume is read in context."
    )
    lines.append("")

    if not summary.counted_findings:
        lines.append("No findings were available to assess for lifecycle concentration.")
        lines.append("")
        if summary.cluster_indicator_findings:
            lines.append(
                f"{summary.cluster_indicator_findings} cluster-indicator finding(s) "
                "were reported separately because they summarise other findings for "
                "the same employee rather than describing an independent concern."
            )
            lines.append("")
        lines.append("---")
        lines.append("")
        return "\n".join(lines)

    lines.append('<table class="summary-table">')
    lines.append("  <thead>")
    lines.append("    <tr><th>Metric</th><th>Value</th></tr>")
    lines.append("  </thead>")
    lines.append("  <tbody>")
    lines.append(
        f"    <tr><td>Findings assessed for concentration</td><td>{summary.counted_findings}</td></tr>"
    )
    lines.append(
        f"    <tr><td>Employees with at least one finding</td><td>{summary.employee_count}</td></tr>"
    )
    lines.append(
        f"    <tr><td>Average findings per affected employee</td>"
        f"<td>{summary.findings_per_employee:.1f}</td></tr>"
    )

    if summary.employees:
        top = summary.employees[0]
        lines.append(
            f"    <tr><td>Largest single-employee share</td>"
            f"<td>{top.finding_count} of {summary.counted_findings} "
            f"({_fmt_pct(summary.top_employee_share)})</td></tr>"
        )

    lines.append(
        f"    <tr><td>Lifecycle themes represented</td><td>{len(summary.theme_counts)}</td></tr>"
    )

    if summary.cluster_indicator_findings:
        lines.append(
            f"    <tr><td>Cluster-indicator findings reported separately</td>"
            f"<td>{summary.cluster_indicator_findings}</td></tr>"
        )

    if summary.unattributed_findings:
        lines.append(
            f"    <tr><td>Findings recorded at organisation level</td>"
            f"<td>{summary.unattributed_findings}</td></tr>"
        )

    lines.append("  </tbody>")
    lines.append("</table>")
    lines.append("")

    if summary.employees:
        lines.append("**Most affected employees**")
        lines.append("")
        lines.append('<table class="summary-table">')
        lines.append("  <thead>")
        lines.append(
            "    <tr><th>Employee</th><th>Findings</th><th>High severity</th>"
            "<th>Modules</th><th>Lifecycle themes</th></tr>"
        )
        lines.append("  </thead>")
        lines.append("  <tbody>")
        for cluster in summary.employees[:top_employees]:
            modules = ", ".join(cluster.modules) or "Not recorded"
            themes = "; ".join(cluster.themes) or "Not classified"
            lines.append(
                f"    <tr><td>{cluster.employee_id}</td><td>{cluster.finding_count}</td>"
                f"<td>{cluster.high_count}</td><td>{modules}</td><td>{themes}</td></tr>"
            )
        lines.append("  </tbody>")
        lines.append("</table>")
        lines.append("")

    lines.append("**Findings by lifecycle theme**")
    lines.append("")
    lines.append('<table class="summary-table">')
    lines.append("  <thead>")
    lines.append("    <tr><th>Lifecycle theme</th><th>Findings</th></tr>")
    lines.append("  </thead>")
    lines.append("  <tbody>")
    for theme, count in summary.theme_counts:
        lines.append(f"    <tr><td>{theme}</td><td>{count}</td></tr>")
    lines.append("  </tbody>")
    lines.append("</table>")
    lines.append("")

    lines.append(
        "Where findings concentrate on a small number of employees or on a single "
        "lifecycle theme, review those employees end to end rather than treating each "
        "finding as a separate matter. Confirming one underlying cause commonly "
        "resolves several findings at once."
    )
    lines.append("")

    if summary.cluster_indicator_findings:
        lines.append(
            "Cluster-indicator findings are derived by counting other findings for the "
            "same employee. They are listed separately above because they describe a "
            "concentration that is already represented by the findings they summarise."
        )
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def load_consolidated_findings(base_output_dir: Path) -> List[Dict[str, str]]:
    path = Path(base_output_dir) / CONSOLIDATED_FINDINGS_FILENAME

    if not path.exists():
        return []

    import csv

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def build_lifecycle_concentration(
    base_output_dir: Path,
    top_employees: int = 5,
) -> str:
    rows: Sequence[Mapping[str, str]] = load_consolidated_findings(base_output_dir)

    if not rows:
        return (
            "_Lifecycle concentration was not assessed for this run, because "
            "consolidated cross-module findings were not available._"
        )

    summary = summarise_lifecycle_concentration(rows)
    return build_lifecycle_concentration_markdown(summary, top_employees=top_employees)
