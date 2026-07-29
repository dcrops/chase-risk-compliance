import pandas as pd
import pytest

from common.date_parsing import (
    DEFAULT_DATE_FORMATS,
    DateFormatConfigError,
    DateParsingError,
    parse_date_series,
    resolve_date_formats,
)


def parse(values, formats=("%d/%m/%Y",), **kwargs):
    return parse_date_series(
        pd.Series(values),
        dataset_name="employees",
        column_name="start_date",
        formats=formats,
        **kwargs,
    )


# --------------------------------------------------------------------------
# Australian day-first dates are no longer read month-first
# --------------------------------------------------------------------------

def test_ambiguous_australian_date_is_parsed_day_first():
    result = parse(["01/02/2024"])

    assert result.tolist() == ["2024-02-01"]


def test_second_ambiguous_australian_date_is_parsed_day_first():
    result = parse(["02/03/2024"])

    assert result.tolist() == ["2024-03-02"]


def test_unambiguous_day_first_date_is_parsed():
    result = parse(["25/12/2024"])

    assert result.tolist() == ["2024-12-25"]


def test_day_first_format_rejects_month_first_values():
    with pytest.raises(DateParsingError) as excinfo:
        parse(["12/25/2024"])

    assert "'12/25/2024'" in str(excinfo.value)


# --------------------------------------------------------------------------
# ISO dates
# --------------------------------------------------------------------------

def test_iso_dates_are_parsed_under_the_default_contract():
    result = parse(["2024-02-01", "2024-03-02"], formats=DEFAULT_DATE_FORMATS)

    assert result.tolist() == ["2024-02-01", "2024-03-02"]


def test_iso_values_are_not_lost_when_a_column_mixes_declared_formats():
    result = parse(
        ["2024-02-01", "01/02/2024"],
        formats=("%Y-%m-%d", "%d/%m/%Y"),
    )

    assert result.tolist() == ["2024-02-01", "2024-02-01"]


def test_declared_format_order_does_not_lose_values():
    result = parse(
        ["01/02/2024", "2024-02-01"],
        formats=("%d/%m/%Y", "%Y-%m-%d"),
    )

    assert result.tolist() == ["2024-02-01", "2024-02-01"]


def test_mixed_formats_are_rejected_when_not_declared():
    with pytest.raises(DateParsingError) as excinfo:
        parse(["2024-02-01", "01/02/2024"], formats=("%Y-%m-%d",))

    message = str(excinfo.value)
    assert "'01/02/2024'" in message
    assert "%Y-%m-%d" in message


# --------------------------------------------------------------------------
# Failure messages
# --------------------------------------------------------------------------

def test_failure_message_identifies_dataset_column_format_and_values():
    with pytest.raises(DateParsingError) as excinfo:
        parse(["31/31/2024"], formats=("%d/%m/%Y",))

    message = str(excinfo.value)
    assert "employees" in message
    assert "start_date" in message
    assert "%d/%m/%Y" in message
    assert "'31/31/2024'" in message


def test_failure_message_caps_the_number_of_reported_values():
    values = [f"{i:02d}/99/2024" for i in range(1, 12)]

    with pytest.raises(DateParsingError) as excinfo:
        parse(values)

    assert "further distinct value(s)" in str(excinfo.value)


def test_invalid_values_are_not_silently_coerced_to_null():
    with pytest.raises(DateParsingError):
        parse(["01/02/2024", "not a date"])


# --------------------------------------------------------------------------
# Nulls and blanks
# --------------------------------------------------------------------------

def test_null_and_blank_values_remain_acceptable():
    result = parse([None, "", "   ", "01/02/2024"])

    assert result.tolist()[:3] == [None, None, None] or pd.isna(result.iloc[0])
    assert result.iloc[3] == "2024-02-01"


def test_a_fully_null_column_is_allowed_when_not_required():
    result = parse([None, ""])

    assert result.notna().sum() == 0


def test_a_fully_null_column_fails_when_required():
    with pytest.raises(DateParsingError) as excinfo:
        parse([None, ""], required=True)

    assert "required" in str(excinfo.value)


# --------------------------------------------------------------------------
# Format resolution from the mapping
# --------------------------------------------------------------------------

def test_default_format_is_iso_when_the_mapping_declares_nothing():
    assert resolve_date_formats({}, "employees", "start_date") == ["%Y-%m-%d"]
    assert resolve_date_formats(None, "employees", "start_date") == ["%Y-%m-%d"]


def test_top_level_format_applies_to_every_dataset():
    mapping = {"date_format": "%d/%m/%Y", "employees": {}}

    assert resolve_date_formats(mapping, "employees", "start_date") == ["%d/%m/%Y"]
    assert resolve_date_formats(mapping, "pay_events", "pay_date") == ["%d/%m/%Y"]


def test_dataset_format_overrides_the_top_level_format():
    mapping = {
        "date_format": "%d/%m/%Y",
        "leave_ledger": {"date_format": "%Y-%m-%d"},
    }

    assert resolve_date_formats(mapping, "leave_ledger", "event_date") == ["%Y-%m-%d"]
    assert resolve_date_formats(mapping, "employees", "start_date") == ["%d/%m/%Y"]


def test_column_format_overrides_the_dataset_format():
    mapping = {
        "employees": {
            "date_format": "%d/%m/%Y",
            "date_formats": {"start_date": "%d-%b-%Y"},
        }
    }

    assert resolve_date_formats(mapping, "employees", "start_date") == ["%d-%b-%Y"]


def test_a_column_may_declare_several_formats():
    mapping = {"employees": {"date_formats": {"start_date": ["%d/%m/%Y", "%Y-%m-%d"]}}}

    assert resolve_date_formats(mapping, "employees", "start_date") == [
        "%d/%m/%Y",
        "%Y-%m-%d",
    ]


@pytest.mark.parametrize(
    "declared",
    [
        {"date_format": 20240201},
        {"date_format": ""},
        {"date_format": "dd/mm/yyyy"},
        {"date_format": []},
        {"date_formats": "%d/%m/%Y"},
        {"date_formats": {"start_date": None}},
    ],
)
def test_malformed_date_format_declarations_are_rejected(declared):
    mapping = {"employees": declared}

    with pytest.raises(DateFormatConfigError):
        resolve_date_formats(mapping, "employees", "start_date")


def test_parsing_without_declared_formats_is_rejected():
    with pytest.raises(DateFormatConfigError):
        parse(["01/02/2024"], formats=())
