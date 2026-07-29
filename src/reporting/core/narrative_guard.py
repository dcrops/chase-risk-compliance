from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class NarrativeMetrics:
    total: int
    high: int
    medium: int
    low: int
    structural: int = 0
    logical: int = 0
    contextual: int = 0
    coverage: str = "unknown"  # "full", "partial", "limited", "unknown"


PROHIBITED_PHRASES = [
    "payroll outcomes may not be reliable",
    "system is reliable",
    "system is unreliable",
    "primary driver of risk",
    "strongest area of exposure",
]

RESTRICTED_TERMS = {
    "financial exposure": "requires_exposure_data",
    "material risk": "requires_high_threshold",
    "high risk": "requires_high_threshold",
    "significant risk": "requires_high_threshold",
    "strongest concentration of risk": "requires_ranked_threshold",
    "dominant risk area": "requires_ranked_threshold",
}


def build_severity_interpretation(m: NarrativeMetrics) -> str:
    if m.total == 0:
        return (
            "No findings were identified based on the supplied data. "
            "This does not confirm absence of issues, only that no conditions were triggered."
        )

    if m.high == 0:
        return (
            f"{m.total} findings were identified, none of which are classified as HIGH severity. "
            "Identified issues are limited to lower-severity conditions."
        )

    high_ratio = m.high / m.total

    if high_ratio >= 0.6:
        return (
            f"{m.total} findings were identified, including {m.high} HIGH severity items. "
            "HIGH severity findings account for a substantial share of the overall findings profile."
        )

    if high_ratio >= 0.4:
        return (
            f"{m.total} findings were identified, including {m.high} HIGH severity items. "
            "HIGH severity findings represent a significant proportion of total findings."
        )

    return (
        f"{m.total} findings were identified, including {m.high} HIGH severity items. "
        "HIGH severity findings are present but do not dominate the overall distribution."
    )


def build_severity_distribution_line(m: NarrativeMetrics) -> str:
    if m.total == 0:
        return "No findings available for severity distribution."

    return (
        f"Findings distribution: {m.high} HIGH, {m.medium} MEDIUM, {m.low} LOW "
        f"(Total: {m.total})."
    )


def build_classification_interpretation(m: NarrativeMetrics) -> str:
    total_class = m.structural + m.logical + m.contextual

    if total_class == 0:
        return "Classification breakdown not available."

    buckets = {
        "STRUCTURAL": m.structural,
        "LOGICAL": m.logical,
        "CONTEXTUAL": m.contextual,
    }
    dominant = max(buckets, key=buckets.get)
    dominant_count = buckets[dominant]
    dominant_ratio = dominant_count / total_class if total_class else 0

    if dominant_ratio >= 0.6:
        return (
            f"The findings profile is strongly concentrated in {dominant.lower()} items."
        )

    return f"The findings profile is primarily concentrated in {dominant.lower()} items."


def build_coverage_statement(m: NarrativeMetrics) -> str:
    if m.coverage == "limited":
        return (
            "Assessment coverage is limited based on the data provided. "
            "Certain risk areas may not be fully assessable without additional datasets."
        )

    if m.coverage == "partial":
        return (
            "Assessment coverage is partial. Some risk areas may require additional data "
            "to fully evaluate."
        )

    if m.coverage == "full":
        return "Assessment coverage reflects all datasets supplied for this review."

    return "Coverage level could not be determined from available inputs."


def build_recommendation_summary(m: NarrativeMetrics) -> str:
    if m.total == 0:
        return (
            "No immediate remediation actions are indicated based on triggered findings. "
            "Periodic review is recommended to maintain assurance."
        )

    if m.high > 0:
        return (
            "Prioritise review of HIGH severity findings, followed by broader validation "
            "of related processes and data inputs."
        )

    return (
        "Review identified findings and confirm whether they reflect data limitations, "
        "process issues, or expected system behaviour."
    )


# -----------------------------
# Stronger language (controlled)
# -----------------------------

def build_calibrated_risk_line(m: NarrativeMetrics) -> str:
    """
    Allows stronger wording only when severity mix supports it.
    """
    if m.total == 0:
        return (
            "No triggered findings were identified in this review, so no elevated findings profile was observed."
        )

    high_ratio = m.high / m.total if m.total else 0
    medium_ratio = m.medium / m.total if m.total else 0

    if m.high >= 5 and high_ratio >= 0.5:
        return (
            f"HIGH severity findings account for {round(high_ratio * 100)}% of results, "
            "indicating an elevated findings profile that should be prioritised for review."
        )

    if m.high >= 3 and high_ratio >= 0.4:
        return (
            f"HIGH severity findings account for {round(high_ratio * 100)}% of results, "
            "indicating a materially elevated concentration of higher-severity findings."
        )

    if m.high > 0:
        return (
            f"HIGH severity findings account for {round(high_ratio * 100)}% of results, "
            "but do not represent the majority of findings."
        )

    if m.medium > 0 and medium_ratio >= 0.5:
        return (
            f"MEDIUM severity findings account for {round(medium_ratio * 100)}% of results, "
            "indicating a broader pattern of issues requiring follow-up."
        )

    return "The findings profile is weighted toward lower-severity conditions."


def build_calibrated_module_focus_line(
    top_modules: List[str],
    module_labels: Dict[str, str],
    m: NarrativeMetrics,
) -> str:
    friendly = [module_labels.get(x, x) for x in top_modules[:2]]

    if not friendly:
        return "No module concentration of HIGH severity findings was identified."

    high_ratio = m.high / m.total if m.total else 0

    if len(friendly) >= 2:
        if m.high >= 3 and high_ratio >= 0.4:
            return (
                f"HIGH severity findings were concentrated most heavily in {friendly[0]} and {friendly[1]}."
            )
        return (
            f"HIGH severity findings were identified most often in {friendly[0]} and {friendly[1]}."
        )

    if m.high >= 3 and high_ratio >= 0.4:
        return f"HIGH severity findings were concentrated most heavily in {friendly[0]}."

    return f"HIGH severity findings were identified most often in {friendly[0]}."


# -----------------------------
# Validation
# -----------------------------

def validate_narrative_output(
    text: str,
    m: NarrativeMetrics,
    *,
    has_exposure_data: bool = False,
) -> List[str]:
    errors: List[str] = []
    lower = text.lower()

    for phrase in PROHIBITED_PHRASES:
        if phrase in lower:
            errors.append(f"Prohibited phrase detected: '{phrase}'")

    for phrase, rule in RESTRICTED_TERMS.items():
        if phrase in lower:
            if rule == "requires_exposure_data" and not has_exposure_data:
                errors.append(
                    f"Restricted phrase '{phrase}' requires actual exposure data."
                )
            elif rule == "requires_high_threshold":
                high_ratio = (m.high / m.total) if m.total else 0
                if not (m.high >= 3 and high_ratio >= 0.4):
                    errors.append(
                        f"Restricted phrase '{phrase}' is stronger than supported by the severity profile."
                    )
            elif rule == "requires_ranked_threshold":
                high_ratio = (m.high / m.total) if m.total else 0
                if not (m.high >= 3 and high_ratio >= 0.4):
                    errors.append(
                        f"Restricted comparative phrase '{phrase}' is not justified by current thresholds."
                    )

    if m.high == 0 and "high risk" in lower:
        errors.append("Overstatement: 'high risk' used with no HIGH findings.")

    if m.total == 0 and ("no issues" in lower or "system is stable" in lower):
        errors.append("False assurance: no findings does not confirm absence of issues.")

    if m.coverage in {"partial", "limited"} and "no risk" in lower:
        errors.append("False assurance: incomplete coverage cannot support 'no risk' language.")

    return errors


def ensure_valid_narrative(
    text: str,
    m: NarrativeMetrics,
    *,
    has_exposure_data: bool = False,
) -> None:
    errors = validate_narrative_output(
        text,
        m,
        has_exposure_data=has_exposure_data,
    )
    if errors:
        raise ValueError("Narrative validation failed:\n" + "\n".join(errors))


def validate_report_text(
    report_text: str,
    m: NarrativeMetrics,
    *,
    has_exposure_data: bool = False,
) -> List[str]:
    return validate_narrative_output(
        report_text,
        m,
        has_exposure_data=has_exposure_data,
    )


def ensure_valid_report_text(
    report_text: str,
    m: NarrativeMetrics,
    *,
    has_exposure_data: bool = False,
) -> None:
    errors = validate_report_text(
        report_text,
        m,
        has_exposure_data=has_exposure_data,
    )
    if errors:
        raise ValueError("Report-level narrative validation failed:\n" + "\n".join(errors))