"""RKEG-PAY-006: ordinary earnings recorded without a base rate.

Rewritten from the retired ``rkeg.engine`` harness onto the current rule
configuration and detector registry. The assertion is unchanged: the rule must
stay live against the sample dataset.
"""


def test_pay_006_missing_base_rate_produces_findings(run_sample_rule):
    findings = run_sample_rule("RKEG-PAY-006")

    assert findings, "Expected RKEG-PAY-006 to produce findings for sample data"
    assert all(f.rule_code == "RKEG-PAY-006" for f in findings)
    assert all(f.finding_id for f in findings)


def test_pay_006_findings_are_stable_across_reruns(run_sample_rule):
    first = run_sample_rule("RKEG-PAY-006")
    second = run_sample_rule("RKEG-PAY-006")

    assert [f.finding_id for f in first] == [f.finding_id for f in second]
