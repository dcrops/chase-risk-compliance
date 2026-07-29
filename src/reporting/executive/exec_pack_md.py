from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Dict, Optional

import json
from dataclasses import dataclass
from datetime import date, datetime
from zoneinfo import ZoneInfo

from common.severity import SEVERITY_BY_CODE
from reporting.core.report_text import scan_report_text
from reporting.core.paths import get_repo_root, get_default_outputs_dir
from reporting.core.review_period import derive_review_period_from_windows
from reporting.core.structure import ReportStructure
from reporting.rkeg_text import build_rkeg_severity_overview_table
from reporting.sections.exec_pack_sections import (
    build_scope_intro,
    build_scope_leave,
    build_scope_lsl,
    build_scope_term,
    build_scope_rkeg,
    build_scope_cross_module,
    build_scope_and_methodology,
    build_leave_no_findings_message,
    build_term_no_findings_message,
    build_rkeg_no_findings_message,
    build_cross_no_findings_message,
    build_lsl_no_findings_message,
    build_lsl_coverage_note,
    build_rkeg_summary,
    build_lsl_severity_summary,
    build_term_severity_summary,
    build_cross_module_summary,
    build_limitations,
    build_next_steps,
    build_appendices,
)

from reporting.core.cover_page import build_cover_page
from reporting.executive.lifecycle_clusters import build_lifecycle_concentration

from reporting.core.narrative_guard import (
    NarrativeMetrics,
    build_severity_interpretation,
    build_severity_distribution_line,
    build_classification_interpretation,
    build_coverage_statement,
    build_recommendation_summary,
    ensure_valid_narrative,
    build_calibrated_risk_line,
    build_calibrated_module_focus_line,
    ensure_valid_report_text,
)


MELBOURNE_TZ = ZoneInfo("Australia/Melbourne")
report_date = datetime.now(MELBOURNE_TZ).strftime("%d %b %Y")

# ---------- Engagement scope ----------

MODULE_LEAVE = "LEAVE"
MODULE_LSL = "LSL"
MODULE_TERM = "TERM"
MODULE_RKEG = "RKEG"
MODULE_CROSS = "CROSS_MODULE"

MODULE_ORDER = [MODULE_LEAVE, MODULE_LSL, MODULE_TERM, MODULE_RKEG, MODULE_CROSS]

MODULE_LABELS = {
    MODULE_LEAVE: "Leave & Entitlement Leakage (LEAVE)",
    MODULE_LSL: "Long Service Leave Exposure (LSL)",
    MODULE_TERM: "Termination Exposure (TERM)",
    MODULE_RKEG: "Record-Keeping & Evidence Gaps (RKEG)",
    MODULE_CROSS: "Cross-Module Integrity (CROSS_MODULE)",
}

DEFAULT_MODULES = [MODULE_LEAVE, MODULE_LSL, MODULE_TERM, MODULE_RKEG, MODULE_CROSS]

# ---------- Paths ----------

BASE_DIR = get_repo_root()
OUTPUTS_DIR = get_default_outputs_dir()

LEAVE_FINDINGS_CSV = OUTPUTS_DIR / "leave_leakage_findings.csv"
LEAKAGE_REPORT_CSV = OUTPUTS_DIR / "leakage_report.csv"

RKEG_SUMMARY_BY_SEVERITY_CSV = OUTPUTS_DIR / "rkeg_summary_by_severity.csv"
RKEG_FINDINGS_CSV = OUTPUTS_DIR / "rkeg_findings.csv"

TERM_SUMMARY_BY_SEVERITY_CSV = OUTPUTS_DIR / "term_summary_by_severity.csv"
TERM_FINDINGS_CSV = OUTPUTS_DIR / "term_findings.csv"

LSL_FINDINGS_CSV = OUTPUTS_DIR / "lsl_findings.csv"
LSL_SUMMARY_BY_SEVERITY_CSV = OUTPUTS_DIR / "lsl_summary_by_severity.csv"

LEAVE_DATA_WINDOW_CSV = OUTPUTS_DIR / "leave_data_window.csv"
LSL_DATA_WINDOW_CSV = OUTPUTS_DIR / "lsl_data_window.csv"
TERM_DATA_WINDOW_CSV = OUTPUTS_DIR / "term_data_window.csv"
RKEG_DATA_WINDOW_CSV = OUTPUTS_DIR / "rkeg_data_window.csv"

EXEC_PACK_MD_PATH = OUTPUTS_DIR / "crc_executive_pack.md"

# ---------- Data models ----------


@dataclass
class Finding:
    rule_code: str
    severity: str
    classification: str
    employee_id: str
    leave_type: str
    as_of_date: str
    message: str

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> "Finding":
        return cls(
            rule_code=row.get("rule_code") or row.get("rule_id") or "",
            severity=(row.get("severity", "") or "").upper(),
            classification=(row.get("classification", "") or "").upper(),
            employee_id=row.get("employee_id", ""),
            leave_type=row.get("leave_type", ""),
            as_of_date=row.get("as_of_date", ""),
            message=row.get("message") or row.get("description") or "",
        )


@dataclass
class ExposureRow:
    label: str
    amount: float

    @classmethod
    def from_row(cls, row: Dict[str, str]) -> Optional["ExposureRow"]:
        label = row.get("label") or row.get("rule_code") or row.get("bucket") or ""
        amount_field_candidates = [
            "estimated_exposure",
            "exposure_amount",
            "leakage_amount",
            "amount",
            "value",
        ]

        amount_value: Optional[float] = None
        for field in amount_field_candidates:
            if field in row and row[field]:
                try:
                    amount_value = float(row[field])
                    break
                except ValueError:
                    continue

        if amount_value is None:
            return None

        return cls(label=label, amount=amount_value)


# ---------- CSV helpers ----------

def load_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []

    import csv

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _load_csv(path: Path) -> List[Dict[str, str]]:
    return load_csv(path)


def load_findings() -> List[Finding]:
    rows = load_csv(LEAVE_FINDINGS_CSV)
    return [Finding.from_row(r) for r in rows]


def load_exposure_rows() -> List[ExposureRow]:
    rows = load_csv(LEAKAGE_REPORT_CSV)
    exposure_rows: List[ExposureRow] = []
    for r in rows:
        er = ExposureRow.from_row(r)
        if er is not None:
            exposure_rows.append(er)
    return exposure_rows


# ---------- Review period helpers ----------

def _parse_iso_date(s: str | None) -> Optional[date]:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    try:
        return date.fromisoformat(s)
    except ValueError:
        return None


def _derive_review_period(findings: List[Finding]) -> str:
    dates: List[date] = []
    for f in findings:
        d = _parse_iso_date(f.as_of_date)
        if d is not None:
            dates.append(d)

    if not dates:
        return "Review period not clearly identifiable from supplied data"

    start = min(dates)
    end = max(dates)

    if start == end:
        return start.strftime("%d %b %Y")

    return f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"


def _module_ran(module: str, base_output_dir: Path) -> bool:
    if module == MODULE_LEAVE:
        return (
            (base_output_dir / "leave_leakage_findings.csv").exists()
            or (base_output_dir / "leakage_report.csv").exists()
        )
    if module == MODULE_LSL:
        return (
            (base_output_dir / "lsl_summary_by_severity.csv").exists()
            or (base_output_dir / "lsl_findings.csv").exists()
        )
    if module == MODULE_TERM:
        return (
            (base_output_dir / "term_summary_by_severity.csv").exists()
            or (base_output_dir / "term_findings.csv").exists()
        )
    if module == MODULE_RKEG:
        return (
            (base_output_dir / "rkeg_summary_by_severity.csv").exists()
            or (base_output_dir / "rkeg_findings.csv").exists()
        )
    if module == MODULE_CROSS:
        return (
            (base_output_dir / "cross_module_findings.csv").exists()
            or (base_output_dir / "cross_module_summary.csv").exists()
        )
    return False


def _derive_exec_review_period(included_modules: set[str], base_output_dir: Path) -> str:
    modules_dir = base_output_dir

    candidate_paths = []

    if MODULE_LEAVE in included_modules:
        candidate_paths.append(modules_dir / "leave_leakage_findings.csv")
    if MODULE_LSL in included_modules:
        candidate_paths.append(modules_dir / "lsl_findings.csv")
    if MODULE_TERM in included_modules:
        candidate_paths.append(modules_dir / "term_findings.csv")
    if MODULE_RKEG in included_modules:
        candidate_paths.append(modules_dir / "rkeg_findings.csv")
    if MODULE_CROSS in included_modules:
        candidate_paths.append(modules_dir / "cross_module_findings.csv")

    all_dates: list[date] = []

    for path in candidate_paths:
        if not path.exists():
            continue

        rows = _load_csv(path)

        for row in rows:
            for col, raw in row.items():
                if not col or "date" not in col.lower():
                    continue

                value = (raw or "").strip()
                if not value:
                    continue

                for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                    try:
                        d = datetime.strptime(value, fmt).date()
                        all_dates.append(d)
                        break
                    except ValueError:
                        continue

    if not all_dates:
        return "Review period not clearly identifiable from supplied module outputs"

    start = min(all_dates)
    end = max(all_dates)

    if start == end:
        return start.strftime("%d %b %Y")

    return f"{start.strftime('%d %b %Y')} to {end.strftime('%d %b %Y')}"


def derive_exec_review_period_from_data(included_modules: set[str], base_output_dir: Path) -> str:
    modules_dir = base_output_dir

    window_paths: list[Path] = []

    if MODULE_LEAVE in included_modules:
        window_paths.append(modules_dir / "leave_data_window.csv")
    if MODULE_LSL in included_modules:
        window_paths.append(modules_dir / "lsl_data_window.csv")
    if MODULE_TERM in included_modules:
        window_paths.append(modules_dir / "term_data_window.csv")
    if MODULE_RKEG in included_modules:
        window_paths.append(modules_dir / "rkeg_data_window.csv")
    if MODULE_CROSS in included_modules:
        window_paths.append(modules_dir / "cross_module_data_window.csv")

    period_from_windows = derive_review_period_from_windows(
        window_paths,
        fallback=None,
    )

    if period_from_windows:
        return period_from_windows

    return _derive_exec_review_period(included_modules, base_output_dir)


# ---------- Module helpers ----------

def normalise_modules(included_modules: set[str] | list[str] | None) -> set[str]:
    return {m.strip().upper() for m in (included_modules or [])}


def included_modules_in_order(included_modules: set[str] | list[str] | None) -> list[str]:
    mods = normalise_modules(included_modules)
    return [m for m in MODULE_ORDER if m in mods]


def _friendly_module_label(module_code: str) -> str:
    labels = {
        "TERM": "Termination Exposure",
        "RKEG": "Record-Keeping & Evidence Gaps",
        "LEAVE": "Leave & Entitlement Leakage",
        "LSL": "Long Service Leave Exposure",
        "CROSS_MODULE": "Cross-Module Integrity",
    }
    return labels.get((module_code or "").upper(), module_code or "Unknown")

def _build_exec_narrative_metrics(summary: Dict) -> NarrativeMetrics:
    class_summary = summary.get("class_summary", {}) or {}
    severity_summary = summary.get("severity_summary", {}) or {}

    return NarrativeMetrics(
        total=int(summary.get("total_findings", 0) or 0),
        high=int(severity_summary.get("HIGH", 0) or 0),
        medium=int(severity_summary.get("MEDIUM", 0) or 0),
        low=int(severity_summary.get("LOW", 0) or 0),
        structural=int(class_summary.get("STRUCTURAL", 0) or 0),
        logical=int(class_summary.get("LOGICAL", 0) or 0),
        contextual=int(class_summary.get("CONTEXTUAL", 0) or 0),
        coverage="full",
    )

# ---------- Executive summary / risk profile ----------

def print_exec_pack_preflight(base_output_dir: Path, included_modules: set[str]) -> None:
    executive_md = base_output_dir / "executive" / "executive_summary.md"
    executive_json = base_output_dir / "executive" / "executive_summary.json"

    print("Exec Pack preflight:")
    print(f" - output_dir: {base_output_dir}")
    print(f" - executive_summary.md: {executive_md.exists()}")
    print(f" - executive_summary.json: {executive_json.exists()}")
    print(f" - included modules: {sorted(included_modules)}")

    modules_dir = base_output_dir
    for module in included_modules_in_order(included_modules):
        if module == "LEAVE":
            print(f" - LEAVE findings: {(modules_dir / 'leave_leakage_findings.csv').exists()}")
        elif module == "LSL":
            print(f" - LSL findings: {(modules_dir / 'lsl_findings.csv').exists()}")
            print(f" - LSL severity summary: {(modules_dir / 'lsl_summary_by_severity.csv').exists()}")
        elif module == "TERM":
            print(f" - TERM findings: {(modules_dir / 'term_findings.csv').exists()}")
            print(f" - TERM severity summary: {(modules_dir / 'term_summary_by_severity.csv').exists()}")
        elif module == "RKEG":
            print(f" - RKEG findings: {(modules_dir / 'rkeg_findings.csv').exists()}")
            print(f" - RKEG severity summary: {(modules_dir / 'rkeg_summary_by_severity.csv').exists()}")
        elif module == "CROSS_MODULE":
            print(f" - CROSS_MODULE findings: {(modules_dir / 'cross_module_findings.csv').exists()}")
            print(f" - CROSS_MODULE severity summary: {(modules_dir / 'cross_module_summary_by_severity.csv').exists()}")


def load_executive_summary_md(base_output_dir: Path) -> str:
    path = base_output_dir / "executive" / "executive_summary.md"

    if not path.exists():
        print(f"⚠ Missing executive summary markdown: {path}")
        return (
            "_Executive summary not available for this run. "
            "Generate the executive summary layer before building the Exec Pack._"
        )

    text = path.read_text(encoding="utf-8").strip()

    lines = text.splitlines()

    if lines and lines[0].strip().startswith("#"):
        lines = lines[1:]

        if lines and not lines[0].strip():
            lines = lines[1:]

    return "\n".join(lines).strip()


def load_optional_markdown(path: Path, drop_first_h1: bool = False) -> str:
    if not path.exists():
        return ""

    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return ""

    if drop_first_h1:
        lines = text.splitlines()
        if lines and lines[0].startswith("# "):
            text = "\n".join(lines[1:]).lstrip()

    return text.strip()


def load_executive_summary_json(base_output_dir: Path) -> Dict:
    path = base_output_dir / "executive" / "executive_summary.json"
    if not path.exists():
        print(f"⚠ Missing executive summary JSON: {path}")
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_executive_summary(base_output_dir: Path) -> str:
    return load_executive_summary_md(base_output_dir)


def build_highlight_insights(base_output_dir: Path) -> str:
    summary = load_executive_summary_json(base_output_dir)
    if not summary:
        return "_Highlight insights not available for this run._"

    metrics = _build_exec_narrative_metrics(summary)
    top_high_modules = summary.get("top_high_modules", []) or []

    narrative_labels = {
        "TERM": "termination handling",
        "RKEG": "record-keeping controls",
        "LEAVE": "leave calculation and balance integrity",
        "LSL": "long service leave eligibility and accrual",
        "CROSS_MODULE": "cross-module lifecycle consistency",
    }

    severity_line = build_severity_interpretation(metrics)
    distribution_line = build_severity_distribution_line(metrics)
    classification_line = build_classification_interpretation(metrics)
    calibrated_risk_line = build_calibrated_risk_line(metrics)
    module_line = build_calibrated_module_focus_line(
        top_modules=top_high_modules,
        module_labels=narrative_labels,
        m=metrics,
    )

    for line in [
        severity_line,
        distribution_line,
        classification_line,
        calibrated_risk_line,
        module_line,
    ]:
        ensure_valid_narrative(line.replace("**", ""), metrics)

    lines: List[str] = []
    lines.append("The following points summarise the most important observations from the analysis:")
    lines.append("")
    lines.append(f"- {severity_line}")
    lines.append(f"- {distribution_line}")
    lines.append(f"- {classification_line}")
    lines.append(f"- {calibrated_risk_line}")
    lines.append(f"- {module_line}")
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def _fmt_count_pct(count: int, total: int) -> str:
    if not total:
        return str(count)
    pct = round((count / total) * 100)
    return f"{count} ({pct}%)"


def build_risk_profile_overview(base_output_dir: Path) -> str:
    summary = load_executive_summary_json(base_output_dir)
    if not summary:
        return "_Risk profile overview not available for this run._"

    total_findings = summary.get("total_findings", 0)
    class_summary = summary.get("class_summary", {})
    severity_summary = summary.get("severity_summary", {})
    dominant_classification = summary.get("dominant_classification", "Unknown")
    dominant_severity = summary.get("dominant_severity", "Unknown")
    top_high_modules = summary.get("top_high_modules", [])

    logical_count = class_summary.get("LOGICAL", 0)
    structural_count = class_summary.get("STRUCTURAL", 0)
    contextual_count = class_summary.get("CONTEXTUAL", 0)

    high_count = severity_summary.get("HIGH", 0)
    medium_count = severity_summary.get("MEDIUM", 0)
    low_count = severity_summary.get("LOW", 0)

    friendly_modules = [_friendly_module_label(m) for m in top_high_modules]
    if friendly_modules:
        module_text = ", ".join(friendly_modules)
    else:
        module_text = "None identified"

    lines: List[str] = []
    lines.append(
        "This section summarises the overall findings profile across all included modules using the consolidated CRC summary outputs."
    )
    lines.append("")

    lines.append('<table class="summary-table">')
    lines.append("  <thead>")
    lines.append("    <tr><th>Metric</th><th>Value</th></tr>")
    lines.append("  </thead>")
    lines.append("  <tbody>")
    lines.append(f"    <tr><td>Total findings</td><td>{total_findings}</td></tr>")
    lines.append(f"    <tr><td>Dominant classification</td><td>{dominant_classification}</td></tr>")
    lines.append(f"    <tr><td>Dominant severity</td><td>{dominant_severity}</td></tr>")
    lines.append(f"    <tr><td>Logical findings</td><td>{_fmt_count_pct(logical_count, total_findings)}</td></tr>")
    lines.append(f"    <tr><td>Structural findings</td><td>{_fmt_count_pct(structural_count, total_findings)}</td></tr>")
    lines.append(f"    <tr><td>Contextual findings</td><td>{_fmt_count_pct(contextual_count, total_findings)}</td></tr>")
    lines.append(f"    <tr><td>High severity findings</td><td>{_fmt_count_pct(high_count, total_findings)}</td></tr>")
    lines.append(f"    <tr><td>Medium severity findings</td><td>{_fmt_count_pct(medium_count, total_findings)}</td></tr>")
    lines.append(f"    <tr><td>Low severity findings</td><td>{_fmt_count_pct(low_count, total_findings)}</td></tr>")
    lines.append(f"    <tr><td>Modules with most HIGH severity findings</td><td>{module_text}</td></tr>")
    lines.append("  </tbody>")
    lines.append("</table>")
    lines.append("")
    lines.append(
        "Classification is used to distinguish between substantive integrity issues, structural data limitations, and contextual items requiring human judgement."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def build_coverage_data_dependency_insight(base_output_dir: Path) -> str:
    path = base_output_dir / "crc_coverage_insight.md"
    text = load_optional_markdown(path, drop_first_h1=True)

    if not text:
        return "_Coverage and data dependency insight was not generated for this run, as no comparison dataset was provided._"

    intro = """
### What this section shows

This section compares results from two levels of analysis:

- **Payroll-only analysis** - based on core payroll datasets such as pay events, leave balances, and termination records. This provides a high-confidence baseline view of payroll integrity using readily available data.
- **Full analysis** - incorporates additional datasets (such as configuration, supporting records, or extended attributes where available), enabling broader rule coverage and deeper validation of payroll processes.

The difference between these two views reflects **coverage, not prediction**. Additional findings identified in the full analysis represent areas that are not fully assessable using payroll-only data and require broader system context to evaluate.
""".strip()

    return f"{intro}\n\n{text}"


# ---------- Severity loaders ----------

def load_rkeg_severity_counts(base_output_dir: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    modules_dir = base_output_dir

    summary_path = modules_dir / "rkeg_summary_by_severity.csv"
    findings_path = modules_dir / "rkeg_findings.csv"

    summary_rows = _load_csv(summary_path)
    if summary_rows:
        sev_candidates = ["severity", "Severity"]
        count_candidates = ["finding_count", "count", "Count", "n", "N", "value", "Value"]

        first = summary_rows[0]
        sev_col = next((c for c in sev_candidates if c in first), None)
        count_col = next((c for c in count_candidates if c in first), None)

        if sev_col and count_col:
            for r in summary_rows:
                sev = (r.get(sev_col) or "").strip().upper()
                if not sev:
                    continue
                try:
                    n = int(float((r.get(count_col) or "0") or "0"))
                except ValueError:
                    n = 0
                if sev in counts:
                    counts[sev] += n
            return counts

    finding_rows = _load_csv(findings_path)
    for r in finding_rows:
        sev = (r.get("severity") or r.get("Severity") or "").strip().upper()
        if sev in counts:
            counts[sev] += 1

    return counts


def load_lsl_severity_counts(base_output_dir: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    modules_dir = base_output_dir

    summary_path = modules_dir / "lsl_summary_by_severity.csv"
    findings_path = modules_dir / "lsl_findings.csv"

    summary_rows = _load_csv(summary_path)
    if summary_rows:
        sev_candidates = ["severity", "Severity"]
        count_candidates = ["finding_count", "count", "Count", "n", "N", "value", "Value"]

        first = summary_rows[0]
        sev_col = next((c for c in sev_candidates if c in first), None)
        count_col = next((c for c in count_candidates if c in first), None)

        if sev_col and count_col:
            for r in summary_rows:
                sev = (r.get(sev_col) or "").strip().upper()
                try:
                    n = int(float((r.get(count_col) or "0") or "0"))
                except ValueError:
                    n = 0
                if sev in counts:
                    counts[sev] += n
            return counts

    finding_rows = _load_csv(findings_path)
    for r in finding_rows:
        sev = (r.get("severity") or r.get("Severity") or "").strip().upper()
        if sev in counts:
            counts[sev] += 1

    return counts


def load_term_severity_counts(base_output_dir: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    modules_dir = base_output_dir

    summary_path = modules_dir / "term_summary_by_severity.csv"
    findings_path = modules_dir / "term_findings.csv"

    summary_rows = _load_csv(summary_path)
    if summary_rows:
        sev_candidates = ["severity", "Severity"]
        count_candidates = ["finding_count", "count", "Count", "n", "N", "value", "Value"]

        first = summary_rows[0]
        sev_col = next((c for c in sev_candidates if c in first), None)
        count_col = next((c for c in count_candidates if c in first), None)

        if sev_col and count_col:
            for r in summary_rows:
                sev = (r.get(sev_col) or "").strip().upper()
                if not sev:
                    continue
                try:
                    n = int(float((r.get(count_col) or "0") or "0"))
                except ValueError:
                    n = 0
                if sev in counts:
                    counts[sev] += n
            return counts

    finding_rows = _load_csv(findings_path)
    for r in finding_rows:
        sev = (r.get("severity") or r.get("Severity") or "").strip().upper()
        if sev in counts:
            counts[sev] += 1

    return counts


def load_cross_module_severity_counts(base_output_dir: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    summary_path = base_output_dir / "cross_module_summary_by_severity.csv"
    findings_path = base_output_dir / "cross_module_findings.csv"

    summary_rows = _load_csv(summary_path)
    if summary_rows:
        sev_candidates = ["severity", "Severity"]
        count_candidates = ["finding_count", "count", "Count", "n", "N", "value", "Value"]

        first = summary_rows[0]
        sev_col = next((c for c in sev_candidates if c in first), None)
        count_col = next((c for c in count_candidates if c in first), None)

        if sev_col and count_col:
            for r in summary_rows:
                sev = (r.get(sev_col) or "").strip().upper()
                if not sev:
                    continue
                try:
                    n = int(float((r.get(count_col) or "0") or "0"))
                except ValueError:
                    n = 0
                if sev in counts:
                    counts[sev] += n
            return counts

    finding_rows = _load_csv(findings_path)
    for r in finding_rows:
        sev = (r.get("severity") or r.get("Severity") or "").strip().upper()
        if sev in counts:
            counts[sev] += 1

    return counts


# ---------- Sorting ----------

def sort_findings(findings: List[Finding]) -> List[Finding]:
    severity_rank = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    return sorted(
        findings,
        key=lambda f: (
            severity_rank.get(getattr(f, "severity", ""), 99),
            getattr(f, "rule_code", "") or "",
            getattr(f, "employee_id", "") or "",
            getattr(f, "as_of_date", "") or "",
        ),
    )


# ---------- Markdown section builders ----------

def build_header(report_title: str, organisation_name: str, review_period: str) -> str:
    return f"""# {report_title}

**Organisation:** {organisation_name}  
**Review period:** {review_period}  
**Report prepared as at:** {report_date}  

**Important note**

This report highlights potential risk signals and process issues based on the data provided.  
It does not constitute legal, accounting, or industrial relations advice.

---
"""


def _build_report_title(modules: set[str]) -> str:
    if modules == {MODULE_LSL}:
        return "Long Service Leave Exposure Review"
    if modules == {MODULE_TERM}:
        return "Termination Exposure Review"
    if modules == {MODULE_RKEG}:
        return "Record-Keeping & Evidence Gaps Review"
    if modules == {MODULE_LEAVE}:
        return "Leave & Entitlement Leakage Review"
    if modules == {MODULE_CROSS}:
        return "Cross Module Integrity Review"
    return "Payroll Risk & Evidence Review"


def build_interpretation_block_exec(base_output_dir: Path) -> str:
    summary = load_executive_summary_json(base_output_dir)
    if not summary:
        return "_Interpretation not available for this run._"

    # Build metrics
    metrics = _build_exec_narrative_metrics(summary)

    # Build controlled narrative components
    severity_line = build_severity_interpretation(metrics)
    distribution_line = build_severity_distribution_line(metrics)
    classification_line = build_classification_interpretation(metrics)
    coverage_line = build_coverage_statement(metrics)
    recommendation_line = build_recommendation_summary(metrics)

    # Validate all narrative before output
    for line in [
        severity_line,
        distribution_line,
        classification_line,
        coverage_line,
        recommendation_line,
    ]:
        ensure_valid_narrative(line.replace("**", ""), metrics)

    # Assemble output
    lines: List[str] = []
    lines.append(
        "The following interpretation summarises the observed findings profile based on the available data."
    )
    lines.append("")
    lines.append(severity_line)
    lines.append("")
    lines.append(distribution_line)
    lines.append("")
    lines.append(classification_line)
    lines.append("")
    lines.append(coverage_line)
    lines.append("")
    lines.append("### Recommended Focus")
    lines.append("")
    lines.append(recommendation_line)
    lines.append("")
    lines.append(
        "_This interpretation is based on triggered findings and reflects observed patterns in the supplied data. "
        "It does not, on its own, confirm payroll error, non-compliance, or quantified exposure._"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def build_data_sources_section(included_modules: set[str] | list[str] | None, base_output_dir: Path) -> str:
    modules_dir = base_output_dir

    lines: List[str] = []
    lines.append(
        "This review was generated from the following analysis outputs within the project `outputs/` directory:"
    )
    lines.append("")

    mods = normalise_modules(included_modules)
    for m in included_modules_in_order(mods):
        if m == MODULE_LEAVE:
            leave_findings = modules_dir / "leave_leakage_findings.csv"
            leakage_report = base_output_dir / "leakage_report.csv"
            if leave_findings.exists():
                lines.append(f"- `{leave_findings.relative_to(base_output_dir)}`  ")
            if leakage_report.exists():
                lines.append(f"- `{leakage_report.relative_to(base_output_dir)}`  ")

        elif m == MODULE_LSL:
            lsl_summary = modules_dir / "lsl_summary_by_severity.csv"
            lsl_findings = modules_dir / "lsl_findings.csv"
            if lsl_summary.exists():
                lines.append(f"- `{lsl_summary.relative_to(base_output_dir)}`  ")
            if lsl_findings.exists():
                lines.append(f"- `{lsl_findings.relative_to(base_output_dir)}`  ")

        elif m == MODULE_TERM:
            term_summary = modules_dir / "term_summary_by_severity.csv"
            term_findings = modules_dir / "term_findings.csv"
            if term_summary.exists():
                lines.append(f"- `{term_summary.relative_to(base_output_dir)}`  ")
            if term_findings.exists():
                lines.append(f"- `{term_findings.relative_to(base_output_dir)}`  ")

        elif m == MODULE_RKEG:
            rkeg_summary = modules_dir / "rkeg_summary_by_severity.csv"
            rkeg_findings = modules_dir / "rkeg_findings.csv"
            if rkeg_summary.exists():
                lines.append(f"- `{rkeg_summary.relative_to(base_output_dir)}`  ")
            if rkeg_findings.exists():
                lines.append(f"- `{rkeg_findings.relative_to(base_output_dir)}`  ")

        elif m == MODULE_CROSS:
            cross_findings = modules_dir / "cross_module_findings.csv"
            cross_summary = modules_dir / "cross_module_summary_by_severity.csv"
            if cross_summary.exists():
                rel_path = str(cross_summary.relative_to(base_output_dir)).replace("\\", "/")
                lines.append(f"- `{rel_path}`  ")
            if cross_findings.exists():
                rel_path = str(cross_findings.relative_to(base_output_dir)).replace("\\", "/")
                lines.append(f"- `{rel_path}`  ")

    exec_summary_md = base_output_dir / "executive" / "executive_summary.md"
    exec_summary_json = base_output_dir / "executive" / "executive_summary.json"
    if exec_summary_md.exists():
        lines.append(f"- `{exec_summary_md.relative_to(base_output_dir)}`  ")
    if exec_summary_json.exists():
        lines.append(f"- `{exec_summary_json.relative_to(base_output_dir)}`  ")

    coverage_insight_md = base_output_dir / "crc_coverage_insight.md"
    if coverage_insight_md.exists():
        lines.append(f"- `{coverage_insight_md.relative_to(base_output_dir)}`  ")

    lines.append("")
    lines.append(
        "These outputs were produced by rule-based checks over payroll and HR CSV extracts supplied by the organisation for the review period."
    )
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def build_key_findings_overview(findings: List[Finding]) -> str:
    high = sum(1 for f in findings if getattr(f, "severity", "") == "HIGH")
    med = sum(1 for f in findings if getattr(f, "severity", "") == "MEDIUM")
    low = sum(1 for f in findings if getattr(f, "severity", "") == "LOW")

    high_def = SEVERITY_BY_CODE.get("HIGH")
    med_def = SEVERITY_BY_CODE.get("MEDIUM")
    low_def = SEVERITY_BY_CODE.get("LOW")

    high_desc = high_def.description if high_def else "Higher-risk record-keeping or entitlement concern."
    med_desc = med_def.description if med_def else "Material configuration, process, or data concern."
    low_desc = low_def.description if low_def else "Lower-impact data quality or minor process issue."

    return f"""The automated checks identified the following potential issues in the leave and entitlement data reviewed. Severity reflects the relative level of risk to payroll accuracy and audit defensibility, not a confirmed breach.

<table class="summary-table">
  <thead>
    <tr>
      <th>Severity</th>
      <th>Count</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><span class="badge-high">High</span></td>
      <td>{high}</td>
      <td>{high_desc}</td>
    </tr>
    <tr>
      <td><span class="badge-medium">Medium</span></td>
      <td>{med}</td>
      <td>{med_desc}</td>
    </tr>
    <tr>
      <td><span class="badge-low">Low</span></td>
      <td>{low}</td>
      <td>{low_desc}</td>
    </tr>
  </tbody>
</table>

---
""".strip()


# ---------- Orchestrator ----------

def generate_exec_pack(
    organisation_name: str = "Organisation not specified",
    review_period: str | None = None,
    modules: Optional[Iterable[str]] = None,
    output_dir: Path | None = None,
) -> Path:
    """
    Generate crc_executive_pack.md for the supplied output directory.
    """

    target_dir = output_dir or OUTPUTS_DIR

    requested: set[str] = {m.strip().upper() for m in (modules or DEFAULT_MODULES)}
    included: set[str] = {m for m in requested if _module_ran(m, target_dir)}

    report_title: str = _build_report_title(included or requested)

    print("Requested modules:", requested)
    print("Included modules:", included)
    print("Module CSV detection:")
    for m in requested:
        print(" -", m, "=>", _module_ran(m, target_dir))
    print_exec_pack_preflight(target_dir, included)

    leave_findings: List[Finding] = []
    if MODULE_LEAVE in included:
        leave_findings_path = target_dir / "leave_leakage_findings.csv"
        leave_findings = [Finding.from_row(r) for r in load_csv(leave_findings_path)]

    sorted_findings = sort_findings(leave_findings) if leave_findings else []
    rkeg_counts = load_rkeg_severity_counts(target_dir) if MODULE_RKEG in included else {}
    term_counts = load_term_severity_counts(target_dir) if MODULE_TERM in included else {}
    lsl_counts = load_lsl_severity_counts(target_dir) if MODULE_LSL in included else {}
    cross_counts = load_cross_module_severity_counts(target_dir) if MODULE_CROSS in included else {}

    if review_period is None:
        review_period = derive_exec_review_period_from_data(included, target_dir)

    logo_path = (
        Path(__file__).resolve().parents[1] / "assets" / "crc_logo_full.png"
    ).as_uri()

    parts: List[str] = [
        build_cover_page(
            report_title=report_title,
            organisation_name=organisation_name,
            review_period=review_period,
            logo_path=logo_path,
        )
    ]

    structure = ReportStructure()

    structure.add("Executive Summary", 1, build_executive_summary(target_dir))
    structure.add("Highlight Insights", 1, build_highlight_insights(target_dir))
    structure.add("Risk Profile Overview", 1, build_risk_profile_overview(target_dir))
    structure.add(
        "Lifecycle Concentration & Finding Overlap",
        1,
        build_lifecycle_concentration(target_dir),
    )
    structure.add(
        "Coverage & Data Dependency Insight",
        1,
        build_coverage_data_dependency_insight(target_dir),
    )
    structure.add("Data Sources", 1, build_data_sources_section(included, target_dir))
    structure.add(
        "Scope & Methodology",
        1,
        build_scope_intro(MODULE_LABELS, included_modules_in_order(included)),
    )

    if MODULE_LEAVE in included:
        structure.add(
            "Leave & Entitlement Leakage – Scope & Methodology",
            2,
            build_scope_leave(),
        )

    if MODULE_LSL in included:
        structure.add(
            "Long Service Leave (LSL) Exposure – Scope & Methodology",
            2,
            build_scope_lsl(),
        )

    if MODULE_TERM in included:
        structure.add(
            "Termination Exposure – Scope & Methodology",
            2,
            build_scope_term(),
        )

    if MODULE_RKEG in included:
        structure.add(
            "Record-Keeping & Evidence Gaps (RKEG) – Scope & Methodology",
            2,
            build_scope_rkeg(),
        )

    if MODULE_CROSS in included:
        structure.add(
            "Cross-Module Integrity – Scope & Methodology",
            2,
            build_scope_cross_module(),
        )

    summary_modules = {MODULE_LEAVE, MODULE_LSL, MODULE_TERM, MODULE_RKEG, MODULE_CROSS}
    if any(m in included for m in summary_modules):
        structure.add("Module Summary Overview", 1, "")

        if MODULE_LEAVE in included:
            leave_summary_content = (
                build_key_findings_overview(sorted_findings)
                if sorted_findings
                else build_leave_no_findings_message("leave and entitlement")
            )
            structure.add(
                "Leave & Entitlement Leakage (LEAVE) – Summary Overview",
                2,
                leave_summary_content,
            )

        if MODULE_LSL in included:
            lsl_findings_path = target_dir / "lsl_findings.csv"
            lsl_has_data = lsl_findings_path.exists() and bool(load_csv(lsl_findings_path))

            if any(lsl_counts.values()):
                lsl_summary_content = build_lsl_severity_summary(lsl_counts)
                structure.add(
                    "Long Service Leave (LSL) Exposure – Severity Overview",
                    2,
                    lsl_summary_content,
                )
            else:
                lsl_coverage_content = (
                    build_lsl_no_findings_message("long service leave")
                    if lsl_has_data
                    else build_lsl_coverage_note()
                )
                structure.add(
                    "Long Service Leave (LSL) – Coverage Note",
                    2,
                    lsl_coverage_content,
                )

        if MODULE_TERM in included:
            term_summary_content = (
                build_term_severity_summary(term_counts)
                if any(term_counts.values())
                else build_term_no_findings_message("termination-related")
            )
            structure.add(
                "Termination Exposure – Severity Overview",
                2,
                term_summary_content,
            )

        if MODULE_RKEG in included:
            rkeg_summary_content = (
                build_rkeg_summary(rkeg_counts)
                if any(rkeg_counts.values())
                else build_rkeg_no_findings_message("record-keeping and evidence gaps")
            )
            structure.add(
                "Record-Keeping & Evidence Gaps (RKEG) – Severity Overview",
                2,
                rkeg_summary_content,
            )

        if MODULE_CROSS in included:
            cross_summary_content = (
                build_cross_module_summary(cross_counts)
                if any(cross_counts.values())
                else build_cross_no_findings_message("cross-module integrity")
            )
            structure.add(
                "Cross-Module Integrity – Summary Overview",
                2,
                cross_summary_content,
            )

        interpretation_content = build_interpretation_block_exec(target_dir)
        structure.add(
            "How to interpret findings",
            2,
            interpretation_content,
        )

    structure.add("Limitations & Assumptions", 1, build_limitations())
    structure.add("Recommended Next Steps", 1, build_next_steps(target_dir))
    structure.add("Appendices", 1, build_appendices(included, target_dir))

    parts.append(structure.render_markdown())
    final_md = "\n".join(parts)

    summary_for_metrics = load_executive_summary_json(target_dir)
    exec_metrics = _build_exec_narrative_metrics(summary_for_metrics) if summary_for_metrics else NarrativeMetrics(
        total=0,
        high=0,
        medium=0,
        low=0,
        coverage="full",
    )

    ensure_valid_report_text(final_md, exec_metrics)

    scan_result = scan_report_text(final_md)

    if scan_result["hard"]:
        print("⚠ HARD forbidden terms detected in report:")
        print(sorted(set(scan_result["hard"])))

    if scan_result["soft"]:
        print("ℹ Soft-flag terms detected in report:")
        print(sorted(set(scan_result["soft"])))

    md_path = target_dir / "crc_executive_pack.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(final_md, encoding="utf-8")

    print(f"Executive pack generated at: {md_path}")
    return md_path


def generate_leave_leakage_report(
    organisation_name: str = "Organisation not specified",
    review_period: str | None = None,
    modules: Optional[Iterable[str]] = None,
    output_dir: Path | None = None,
) -> Path:
    """
    Backward-compatible wrapper.
    """
    return generate_exec_pack(
        organisation_name=organisation_name,
        review_period=review_period,
        modules=modules,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--organisation-name", default="Organisation not specified")

    args = parser.parse_args()

    path = generate_exec_pack(
        organisation_name=args.organisation_name,
        output_dir=Path(args.output_dir),
        modules=DEFAULT_MODULES,
    )

    print(f"Generated at: {path}")