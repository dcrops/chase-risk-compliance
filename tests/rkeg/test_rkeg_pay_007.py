"""RKEG-PAY-007: negative gross amounts outside recognised adjustment patterns.

Rewritten from the retired ``rkeg.engine`` harness onto the current rule
configuration and detector registry.
"""


def test_pay_007_negative_gross_outside_patterns(run_sample_rule):
    findings = run_sample_rule("RKEG-PAY-007")

    assert findings, "Expected RKEG-PAY-007 to produce findings for sample data"
    assert all(f.rule_code == "RKEG-PAY-007" for f in findings)
    assert all(f.finding_id for f in findings)
