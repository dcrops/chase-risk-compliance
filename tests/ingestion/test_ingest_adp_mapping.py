"""Ingestion of an ADP-shaped extract with non-canonical source headers.

The fixture exercises the whole mapping contract end to end: vendor headers on
the left of `rename`, canonical columns on the right, a run-wide Australian
day-first date format, and one dataset overriding it with ISO.
"""

import json
import shutil
from pathlib import Path

import pandas as pd
import pytest
import yaml

from common.mapping_contract import MappingContractError, validate_mapping
from ingestion import ingest

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "adp"
ADP_MAPPING_PATH = REPO_ROOT / "templates" / "examples" / "adp_column_mapping_example.yaml"


@pytest.fixture
def adp_pilot(tmp_path):
    """A pilot directory laid out the way ingestion expects."""
    pilot_root = tmp_path / "CLT_TEST" / "PILOT_ADP"
    raw_dir = pilot_root / "raw"
    config_dir = pilot_root / "config"
    raw_dir.mkdir(parents=True)
    config_dir.mkdir(parents=True)

    for csv_path in FIXTURE_DIR.glob("*.csv"):
        shutil.copy(csv_path, raw_dir / csv_path.name)

    shutil.copy(ADP_MAPPING_PATH, config_dir / "column_mapping.yaml")

    return pilot_root


@pytest.fixture
def adp_mapping(adp_pilot):
    return ingest.load_mapping(adp_pilot, raw_dir=adp_pilot / "raw")


def test_adp_mapping_validates_against_its_raw_directory(adp_pilot):
    mapping = yaml.safe_load(ADP_MAPPING_PATH.read_text(encoding="utf-8"))

    validate_mapping(mapping, raw_dir=adp_pilot / "raw", mapping_path=ADP_MAPPING_PATH)


def test_employees_are_mapped_into_the_canonical_schema(adp_pilot, adp_mapping):
    employees = ingest.create_employees(adp_pilot / "raw", adp_mapping)

    assert list(employees.columns)[:2] == ["employee_id", "department"]
    assert set(employees["employee_id"]) == {"A001", "A002", "A003"}
    assert "Associate ID" not in employees.columns


def test_day_first_source_dates_are_parsed_day_first(adp_pilot, adp_mapping):
    employees = ingest.create_employees(adp_pilot / "raw", adp_mapping)

    start_dates = dict(zip(employees["employee_id"], employees["start_date"]))

    # 01/02/2024 is 1 February, not 2 January.
    assert start_dates["A001"] == "2024-02-01"
    # 02/03/2024 is 2 March, not 3 February.
    assert start_dates["A002"] == "2024-03-02"
    assert start_dates["A003"] == "2019-07-15"


def test_pay_events_are_mapped_and_dated_day_first(adp_pilot, adp_mapping):
    pay_events = ingest.create_pay_events(adp_pilot / "raw", adp_mapping)

    assert set(pay_events["pay_date"]) == {"2024-02-15", "2024-06-14"}
    assert pay_events["gross_amount"].sum() == pytest.approx(3458.00 + 1558.00 + 4180.00)


def test_terminations_are_mapped_and_dated_day_first(adp_pilot, adp_mapping):
    terminations = ingest.create_terminations(adp_pilot / "raw", adp_mapping)

    assert terminations["employee_id"].tolist() == ["A003"]
    assert terminations["termination_date"].tolist() == ["2024-05-31"]


def test_dataset_level_iso_override_is_honoured(adp_pilot, adp_mapping):
    ledger = ingest.create_leave_ledger(adp_pilot / "raw", adp_mapping)

    assert ledger["event_date"].tolist() == [
        "2024-02-15",
        "2024-03-04",
        "2024-02-15",
        "2024-05-31",
    ]
    assert ledger["leave_type"].tolist() == [
        "ANNUAL_LEAVE",
        "ANNUAL_LEAVE",
        "ANNUAL_LEAVE",
        "LONG_SERVICE_LEAVE",
    ]
    assert ledger["transaction_id"].tolist() == ["T0001", "T0002", "T0003", "T0004"]


def test_leave_snapshot_is_mapped_and_dated_day_first(adp_pilot, adp_mapping):
    snapshot = ingest.create_leave_snapshot(adp_pilot / "raw", adp_mapping)

    assert set(snapshot["as_of_date"]) == {"2024-06-30"}
    assert snapshot["balance_units"].sum() == pytest.approx(45.20 + 12.10 + 180.40)


def test_full_ingestion_run_writes_canonical_processed_files(adp_pilot, monkeypatch):
    monkeypatch.setattr(ingest, "DATA_ROOT", adp_pilot.parents[1])

    ingest.main(client="CLT_TEST", pilot="PILOT_ADP")

    processed = adp_pilot / "processed"
    for name in (
        "employees.csv",
        "terminations.csv",
        "pay_events.csv",
        "leave_ledger.csv",
        "balances_snapshot.csv",
    ):
        assert (processed / name).exists(), name

    employees = pd.read_csv(processed / "employees.csv")
    assert employees.loc[employees["employee_id"] == "A001", "start_date"].item() == "2024-02-01"
    assert employees.loc[employees["employee_id"] == "A003", "employment_status"].item() == "TERMINATED"

    manifest_path = adp_pilot / "outputs" / "run_manifest_ingestion.json"
    assert manifest_path.is_file()
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["module"] == "INGESTION"


def test_ingestion_manifest_excludes_stale_processed_csv(adp_pilot, monkeypatch):
    processed = adp_pilot / "processed"
    processed.mkdir()
    (processed / "stale_unrelated.csv").write_text("old\nvalue\n", encoding="utf-8")
    monkeypatch.setattr(ingest, "DATA_ROOT", adp_pilot.parents[1])

    ingest.main(client="CLT_TEST", pilot="PILOT_ADP")

    manifest = json.loads(
        (adp_pilot / "outputs" / "run_manifest_ingestion.json").read_text(
            encoding="utf-8"
        )
    )
    output_paths = {record["path"] for record in manifest["outputs"]}
    assert "processed/stale_unrelated.csv" not in output_paths


def test_unparseable_date_stops_ingestion_with_an_actionable_message(adp_pilot, adp_mapping):
    register = adp_pilot / "raw" / "ADP_Payroll_Register.csv"
    contents = register.read_text(encoding="utf-8").replace("15/02/2024", "2024-02-15", 1)
    register.write_text(contents, encoding="utf-8")

    with pytest.raises(Exception) as excinfo:
        ingest.create_pay_events(adp_pilot / "raw", adp_mapping)

    message = str(excinfo.value)
    assert "pay_events" in message
    assert "pay_date" in message
    assert "%d/%m/%Y" in message
    assert "2024-02-15" in message


def test_missing_source_file_stops_ingestion_before_any_dataset_is_read(adp_pilot):
    (adp_pilot / "raw" / "ADP_Termination_Report.csv").unlink()

    with pytest.raises(MappingContractError) as excinfo:
        ingest.load_mapping(adp_pilot, raw_dir=adp_pilot / "raw")

    assert "ADP_Termination_Report.csv" in str(excinfo.value)
    assert "was not found" in str(excinfo.value)


def test_load_mapping_can_explicitly_skip_source_file_existence_checks(adp_pilot):
    (adp_pilot / "raw" / "ADP_Termination_Report.csv").unlink()

    mapping = ingest.load_mapping(adp_pilot, check_source_files=False)

    assert mapping["terminations"]["source_file"] == "ADP_Termination_Report.csv"


def test_stale_mapping_format_stops_ingestion(adp_pilot):
    stale = {
        "employees": {
            "source": "ADP_Worker_Demographics.csv",
            "columns": {"employee_id": "Associate ID"},
        }
    }
    (adp_pilot / "config" / "column_mapping.yaml").write_text(
        yaml.safe_dump(stale), encoding="utf-8"
    )

    with pytest.raises(MappingContractError) as excinfo:
        ingest.load_mapping(adp_pilot, raw_dir=adp_pilot / "raw")

    assert "withdrawn template keys" in str(excinfo.value)
