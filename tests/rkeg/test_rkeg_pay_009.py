"""RKEG-PAY-009: gaps or overlaps in recorded rate history.

Rewritten from the retired ``rkeg.engine`` harness onto the current rule
configuration and detector registry.
"""


def test_pay_009_rate_history_gaps_or_overlaps(run_sample_rule):
    findings = run_sample_rule("RKEG-PAY-009")

    assert findings, "Expected RKEG-PAY-009 to produce findings for sample data"
    assert all(f.rule_code == "RKEG-PAY-009" for f in findings)
    assert all(f.finding_id for f in findings)
