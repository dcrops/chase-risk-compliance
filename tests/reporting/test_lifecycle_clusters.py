"""Lifecycle concentration reporting groups findings without changing them.

Several modules examine one lifecycle event from different angles. The
executive pack therefore reports how findings concentrate by employee and by
theme, without suppressing, merging or re-identifying any finding.
"""

from reporting.executive.lifecycle_clusters import (
    CLUSTER_INDICATOR_RULES,
    OTHER_THEME_LABEL,
    build_lifecycle_concentration_markdown,
    summarise_lifecycle_concentration,
    theme_for_rule,
)


def test_theme_lookup_covers_known_lifecycle_rules():
    assert theme_for_rule("TERM-007") == "Leave balances remaining at termination"
    assert theme_for_rule("RKEG-TERM-001") == "Payroll activity after termination"
    assert theme_for_rule("CM-019") == "Lifecycle record structure and completeness"
    assert theme_for_rule("LEAVE-001") == OTHER_THEME_LABEL


def test_concentration_groups_findings_by_employee_without_collapsing_them():
    rows = [
        {"employee_id": "E001", "rule_code": "TERM-007", "severity": "HIGH", "module": "TERM"},
        {"employee_id": "E001", "rule_code": "CM-001", "severity": "HIGH", "module": "CROSS_MODULE"},
        {"employee_id": "E001", "rule_code": "RKEG-TERM-001", "severity": "HIGH", "module": "RKEG"},
        {"employee_id": "E002", "rule_code": "TERM-005", "severity": "MEDIUM", "module": "TERM"},
        {"employee_id": "E002", "rule_code": "CM-020", "severity": "HIGH", "module": "CROSS_MODULE"},
    ]

    summary = summarise_lifecycle_concentration(rows)

    # CM-020 is a derived cluster indicator and is not counted as an independent
    # concern, so the assessed total excludes it.
    assert summary.total_findings == 5
    assert summary.counted_findings == 4
    assert summary.cluster_indicator_findings == 1
    assert summary.employee_count == 2
    assert summary.employees[0].employee_id == "E001"
    assert summary.employees[0].finding_count == 3
    assert summary.employees[0].high_count == 3
    assert "TERM" in summary.employees[0].modules
    assert "CROSS_MODULE" in summary.employees[0].modules


def test_theme_totals_remain_additive():
    rows = [
        {"employee_id": "E001", "rule_code": "TERM-007", "severity": "HIGH", "module": "TERM"},
        {"employee_id": "E001", "rule_code": "TERM-010", "severity": "HIGH", "module": "TERM"},
        {"employee_id": "E002", "rule_code": "LEAVE-001", "severity": "LOW", "module": "LEAVE"},
    ]

    summary = summarise_lifecycle_concentration(rows)
    theme_map = dict(summary.theme_counts)

    assert theme_map["Leave balances remaining at termination"] == 1
    assert theme_map["Payroll activity after termination"] == 1
    assert theme_map[OTHER_THEME_LABEL] == 1
    assert sum(theme_map.values()) == summary.counted_findings


def test_markdown_explains_that_findings_are_not_distinct_events():
    rows = [
        {"employee_id": "E001", "rule_code": "TERM-007", "severity": "HIGH", "module": "TERM"},
        {"employee_id": "E001", "rule_code": "CM-001", "severity": "HIGH", "module": "CROSS_MODULE"},
    ]

    summary = summarise_lifecycle_concentration(rows)
    markdown = build_lifecycle_concentration_markdown(summary)

    assert "not counts of distinct payroll events" in markdown
    assert "Most affected employees" in markdown
    assert "Findings by lifecycle theme" in markdown
    assert "E001" in markdown


def test_cm_020_is_documented_as_a_cluster_indicator():
    assert "CM-020" in CLUSTER_INDICATOR_RULES

    rows = [
        {"employee_id": "E001", "rule_code": "CM-020", "severity": "HIGH", "module": "CROSS_MODULE"},
    ]

    summary = summarise_lifecycle_concentration(rows)
    markdown = build_lifecycle_concentration_markdown(summary)

    assert summary.counted_findings == 0
    assert "cluster-indicator" in markdown.lower()
