import pandas as pd

from rkeg.detectors.leave import run_rule


def _base_rule():
    return {
        "id": "RKEG-LEAVE-001",
        "severity": "HIGH",
        "text": {
            "finding": "Leave ledger movements were detected without corresponding payroll transactions.",
            "remediation": "Reconcile leave taken entries to payroll transactions.",
        },
    }


def test_leave_001_flags_taken_without_same_day_pay_event():
    rule = _base_rule()

    leave_ledger = pd.DataFrame({
        "employee_id": ["E004"],
        "leave_type": ["ANNUAL"],
        "event_date": ["2024-03-20"],
        "units": [-8.0],
        "event_type": ["TAKEN"],
    })

    # Pay event exists for E004, but on a different date (03-15), not 03-20
    pay_events = pd.DataFrame({
        "employee_id": ["E004"],
        "pay_date": ["2024-03-15"],
        "gross_amount": [2000],
    })

    datasets = {"leave_ledger": leave_ledger, "pay_events": pay_events}

    findings = list(run_rule(rule, datasets))

    assert len(findings) == 1
    f = findings[0]
    assert f.rule_code == "RKEG-LEAVE-001"
    assert f.employee_id == "E004"
    assert "matched_pay_event_on_same_date=False" in f.evidence


def test_leave_001_does_not_flag_when_same_day_pay_event_exists():
    rule = _base_rule()

    leave_ledger = pd.DataFrame({
        "employee_id": ["E001"],
        "leave_type": ["ANNUAL"],
        "event_date": ["2024-03-15"],
        "units": [-8.0],
        "event_type": ["TAKEN"],
    })

    pay_events = pd.DataFrame({
        "employee_id": ["E001"],
        "pay_date": ["2024-03-15"],
        "gross_amount": [6000],
    })

    datasets = {"leave_ledger": leave_ledger, "pay_events": pay_events}

    findings = list(run_rule(rule, datasets))
    assert findings == []


def test_leave_001_distinguishes_repeated_identical_ledger_movements():
    """Two identical TAKEN movements are two findings, not one.

    An employee can legitimately record the same leave type, date and units
    twice. Identity therefore has to include the ledger transaction, otherwise
    the second finding silently overwrites the first downstream.
    """
    rule = _base_rule()

    leave_ledger = pd.DataFrame({
        "transaction_id": ["LT-0002", "LT-0006"],
        "employee_id": ["E004", "E004"],
        "leave_type": ["ANNUAL", "ANNUAL"],
        "event_date": ["2024-03-20", "2024-03-20"],
        "units": [-8.0, -8.0],
        "event_type": ["TAKEN", "TAKEN"],
    })

    pay_events = pd.DataFrame({
        "employee_id": ["E004"],
        "pay_date": ["2024-03-15"],
        "gross_amount": [2000],
    })

    datasets = {"leave_ledger": leave_ledger, "pay_events": pay_events}

    findings = list(run_rule(rule, datasets))

    assert len(findings) == 2
    assert len({f.finding_id for f in findings}) == 2


def test_leave_001_distinguishes_identical_movements_without_transaction_ids():
    """Extracts with no transaction_id still produce distinguishable findings."""
    rule = _base_rule()

    leave_ledger = pd.DataFrame({
        "employee_id": ["E004", "E004"],
        "leave_type": ["ANNUAL", "ANNUAL"],
        "event_date": ["2024-03-20", "2024-03-20"],
        "units": [-8.0, -8.0],
        "event_type": ["TAKEN", "TAKEN"],
    })

    pay_events = pd.DataFrame({
        "employee_id": ["E004"],
        "pay_date": ["2024-03-15"],
        "gross_amount": [2000],
    })

    datasets = {"leave_ledger": leave_ledger, "pay_events": pay_events}

    findings = list(run_rule(rule, datasets))

    assert len(findings) == 2
    assert len({f.finding_id for f in findings}) == 2


def test_leave_001_ids_are_stable_across_reruns():
    rule = _base_rule()

    leave_ledger = pd.DataFrame({
        "transaction_id": ["LT-0002"],
        "employee_id": ["E004"],
        "leave_type": ["ANNUAL"],
        "event_date": ["2024-03-20"],
        "units": [-8.0],
        "event_type": ["TAKEN"],
    })

    pay_events = pd.DataFrame({
        "employee_id": ["E004"],
        "pay_date": ["2024-03-15"],
        "gross_amount": [2000],
    })

    datasets = {"leave_ledger": leave_ledger, "pay_events": pay_events}

    first = list(run_rule(rule, datasets))
    second = list(run_rule(rule, datasets))

    assert [f.finding_id for f in first] == [f.finding_id for f in second]


def test_leave_001_ignores_non_taken_events():
    rule = _base_rule()

    # ACCRUAL with no matching pay should NOT trigger LEAVE-001
    leave_ledger = pd.DataFrame({
        "employee_id": ["E001"],
        "leave_type": ["ANNUAL"],
        "event_date": ["2024-03-15"],
        "units": [10.0],
        "event_type": ["ACCRUAL"],
    })

    pay_events = pd.DataFrame({
        "employee_id": ["E001"],
        "pay_date": ["2024-03-15"],
        "gross_amount": [6000],
    })

    datasets = {"leave_ledger": leave_ledger, "pay_events": pay_events}

    findings = list(run_rule(rule, datasets))
    assert findings == []