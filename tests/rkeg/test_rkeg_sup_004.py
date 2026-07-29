"""RKEG-SUP-004: employees without a recorded default superannuation fund.

Rewritten from the retired ``rkeg.engine`` harness onto the current rule
configuration and detector registry. SUP-004 is a tier 2 rule, so this also
covers the fact that ``rkeg.run.main`` executes tier 2.
"""


def test_sup_004_missing_default_fund_produces_findings(run_sample_rule):
    findings = run_sample_rule("RKEG-SUP-004")

    assert findings, "Expected RKEG-SUP-004 to produce at least one sample finding"
    assert all(f.rule_code == "RKEG-SUP-004" for f in findings)
    assert all(f.finding_id for f in findings)


def test_sup_004_findings_are_stable_across_reruns(run_sample_rule):
    first = run_sample_rule("RKEG-SUP-004")
    second = run_sample_rule("RKEG-SUP-004")

    assert [f.finding_id for f in first] == [f.finding_id for f in second]
