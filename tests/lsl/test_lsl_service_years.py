"""LSL service years ignored the canonical termination date.

`prepare_lsl_state` read only `end_date`, so a terminated employee kept
accruing service to the snapshot date. Every eligibility-gated LSL rule
therefore over-stated service for leavers.
"""

import pandas as pd
import pytest

from lsl_exposure.rules import prepare_lsl_state

SNAPSHOT_DATE = pd.Timestamp("2024-03-31")


def state_for(employee_rows: list[dict], snapshot_date=SNAPSHOT_DATE) -> pd.DataFrame:
    return prepare_lsl_state(
        employees=pd.DataFrame(employee_rows),
        snapshot=pd.DataFrame(
            columns=["employee_id", "leave_type", "as_of_date", "balance_units"]
        ),
        pay_rates=None,
        snapshot_date=snapshot_date,
    )


def service_years(state: pd.DataFrame, employee_id: str) -> float:
    row = state[state["employee_id"] == employee_id].iloc[0]
    return float(row["service_years"])


def test_active_employee_accrues_service_to_the_snapshot_date():
    state = state_for([{"employee_id": "A1", "start_date": "2014-03-31"}])

    assert service_years(state, "A1") == pytest.approx(10.0, abs=0.02)


def test_terminated_employee_stops_accruing_at_the_termination_date():
    state = state_for(
        [
            {
                "employee_id": "T1",
                "start_date": "2014-03-31",
                "termination_date": "2019-03-31",
            }
        ]
    )

    assert service_years(state, "T1") == pytest.approx(5.0, abs=0.02)


def test_terminated_employee_no_longer_reaches_the_eligibility_threshold():
    active_state = state_for([{"employee_id": "A1", "start_date": "2014-03-31"}])
    terminated_state = state_for(
        [
            {
                "employee_id": "T1",
                "start_date": "2014-03-31",
                "termination_date": "2018-01-01",
            }
        ]
    )

    assert service_years(active_state, "A1") >= 7.0
    assert service_years(terminated_state, "T1") < 7.0


def test_missing_termination_date_is_treated_as_still_employed():
    state = state_for(
        [
            {
                "employee_id": "A1",
                "start_date": "2014-03-31",
                "termination_date": None,
            }
        ]
    )

    assert service_years(state, "A1") == pytest.approx(10.0, abs=0.02)


def test_legacy_end_date_alias_is_still_honoured():
    state = state_for(
        [{"employee_id": "T1", "start_date": "2014-03-31", "end_date": "2019-03-31"}]
    )

    assert service_years(state, "T1") == pytest.approx(5.0, abs=0.02)


def test_canonical_termination_date_takes_precedence_over_the_legacy_alias():
    state = state_for(
        [
            {
                "employee_id": "T1",
                "start_date": "2014-03-31",
                "termination_date": "2019-03-31",
                "end_date": "2024-03-31",
            }
        ]
    )

    assert service_years(state, "T1") == pytest.approx(5.0, abs=0.02)


def test_historical_snapshot_caps_service_at_the_snapshot_date():
    state = state_for(
        [
            {
                "employee_id": "T1",
                "start_date": "2014-03-31",
                "termination_date": "2024-03-31",
            }
        ],
        snapshot_date=pd.Timestamp("2020-03-31"),
    )

    assert service_years(state, "T1") == pytest.approx(6.0, abs=0.02)


def test_employment_end_date_is_exposed_on_the_state():
    state = state_for(
        [
            {
                "employee_id": "T1",
                "start_date": "2014-03-31",
                "termination_date": "2019-03-31",
            }
        ]
    )

    row = state[state["employee_id"] == "T1"].iloc[0]
    assert row["employment_end_date"] == pd.Timestamp("2019-03-31")


def test_service_years_remain_unknown_without_a_snapshot_date():
    state = state_for(
        [
            {
                "employee_id": "T1",
                "start_date": "2014-03-31",
                "termination_date": "2019-03-31",
            }
        ],
        snapshot_date=None,
    )

    assert pd.isna(state.loc[state["employee_id"] == "T1", "service_years"].iloc[0])


def test_unparseable_termination_date_does_not_abort_state_preparation():
    state = state_for(
        [
            {
                "employee_id": "T1",
                "start_date": "2014-03-31",
                "termination_date": "not-a-date",
            }
        ]
    )

    assert service_years(state, "T1") == pytest.approx(10.0, abs=0.02)
