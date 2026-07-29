import copy
from pathlib import Path

import pytest
import yaml

from common.mapping_contract import MappingContractError, validate_mapping

REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATHS = [
    REPO_ROOT / "templates" / "column_mapping_template.yaml",
    REPO_ROOT / "data" / "clients" / "CLIENT" / "PILOT" / "config" / "column_mapping_template.yaml",
]
ADP_EXAMPLE_PATH = REPO_ROOT / "templates" / "examples" / "adp_column_mapping_example.yaml"


VALID_MAPPING = {
    "employees": {
        "source_file": "worker_extract.csv",
        "rename": {"WorkerID": "employee_id", "HireDt": "start_date"},
    },
    "terminations": {
        "source_file": "separation_register.csv",
        "rename": {"WorkerID": "employee_id", "EndDate": "termination_date"},
    },
    "pay_events": {
        "source_file": "payrun_transactions.csv",
        "rename": {"WorkerID": "employee_id", "PaidOn": "pay_date"},
    },
    "leave_ledger": {
        "source_file": "timeoff_history.csv",
        "rename": {"WorkerID": "employee_id", "EventTS": "event_date"},
    },
}

# The shape committed in the previous templates: `source` plus `columns`, with
# canonical on the left. Ingestion never read it.
STALE_MAPPING = {
    "employees": {
        "source": "employees.csv",
        "columns": {"employee_id": "employee_id", "start_date": "start_date"},
    },
    "terminations": {
        "source": "terminations.csv",
        "columns": {"employee_id": "employee_id", "termination_date": "termination_date"},
    },
    "pay_events": {
        "source": "pay_events.csv",
        "columns": {"employee_id": "employee_id", "pay_date": "pay_date"},
    },
    "leave_ledger": {
        "source": "leave_ledger.csv",
        "columns": {"employee_id": "employee_id", "event_date": "event_date"},
    },
}


def without_raw_dir(mapping):
    validate_mapping(mapping, raw_dir=None, mapping_path=Path("column_mapping.yaml"))


# --------------------------------------------------------------------------
# The active format
# --------------------------------------------------------------------------

def test_valid_active_format_mapping_passes():
    without_raw_dir(VALID_MAPPING)


def test_source_to_canonical_rename_direction_is_accepted():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"]["rename"] = {"HireDt": "start_date"}

    without_raw_dir(mapping)


def test_optional_leave_snapshot_is_accepted():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["leave_snapshot"] = {
        "source_file": "leave_bal_report.csv",
        "rename": {"WorkerID": "employee_id", "CurrentBalanceHrs": "balance"},
    }

    without_raw_dir(mapping)


def test_declared_date_formats_are_accepted():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["date_format"] = "%d/%m/%Y"
    mapping["leave_ledger"]["date_format"] = "%Y-%m-%d"
    mapping["employees"]["date_formats"] = {"start_date": ["%d/%m/%Y", "%Y-%m-%d"]}

    without_raw_dir(mapping)


# --------------------------------------------------------------------------
# The withdrawn template format
# --------------------------------------------------------------------------

def test_stale_template_format_is_rejected_with_migration_guidance():
    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(STALE_MAPPING)

    message = str(excinfo.value)
    assert "source_file" in message
    assert "rename" in message
    assert "opposite direction" in message


def test_stale_format_is_reported_for_every_affected_dataset():
    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(STALE_MAPPING)

    message = str(excinfo.value)
    for dataset in ("employees", "terminations", "pay_events", "leave_ledger"):
        assert dataset in message


# --------------------------------------------------------------------------
# Missing and malformed configuration
# --------------------------------------------------------------------------

def test_missing_required_dataset_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    del mapping["leave_ledger"]

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "leave_ledger" in str(excinfo.value)
    assert "required dataset" in str(excinfo.value)


def test_missing_source_file_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    del mapping["pay_events"]["source_file"]

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "pay_events: 'source_file' is missing" in str(excinfo.value)


def test_missing_rename_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    del mapping["employees"]["rename"]

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "employees: 'rename' is missing" in str(excinfo.value)


def test_invalid_rename_shape_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"]["rename"] = ["WorkerID", "employee_id"]

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "must be a mapping of source column to canonical column" in str(excinfo.value)


def test_empty_rename_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"]["rename"] = {}

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "'rename' is empty" in str(excinfo.value)


def test_duplicate_canonical_targets_are_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"]["rename"] = {
        "WorkerID": "employee_id",
        "StaffNo": "employee_id",
    }

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "mapped from more than one source column" in str(excinfo.value)


def test_unsupported_dataset_key_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"]["column_map"] = {"WorkerID": "employee_id"}

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "unsupported configuration key" in str(excinfo.value)


def test_unrecognised_top_level_key_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["leave_balances"] = {"source_file": "x.csv", "rename": {"a": "b"}}

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "leave_balances" in str(excinfo.value)


def test_dataset_configured_as_a_scalar_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"] = "employees.csv"

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "expected a configuration block" in str(excinfo.value)


def test_empty_mapping_is_reported():
    with pytest.raises(MappingContractError):
        without_raw_dir(None)


def test_invalid_date_format_declaration_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"]["date_formats"] = {"start_date": "dd/mm/yyyy"}

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "not a strptime format" in str(excinfo.value)


def test_date_format_declared_for_a_non_date_column_is_reported():
    mapping = copy.deepcopy(VALID_MAPPING)
    mapping["employees"]["date_formats"] = {"department": "%d/%m/%Y"}

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    assert "is not a canonical date column" in str(excinfo.value)


def test_all_problems_are_reported_together():
    mapping = copy.deepcopy(VALID_MAPPING)
    del mapping["employees"]["source_file"]
    del mapping["pay_events"]["rename"]
    del mapping["leave_ledger"]

    with pytest.raises(MappingContractError) as excinfo:
        without_raw_dir(mapping)

    message = str(excinfo.value)
    assert message.count("  - ") >= 3


# --------------------------------------------------------------------------
# Source file existence
# --------------------------------------------------------------------------

def test_missing_source_file_on_disk_is_reported(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    (raw_dir / "worker_extract.csv").write_text("WorkerID\nE001\n", encoding="utf-8")

    with pytest.raises(MappingContractError) as excinfo:
        validate_mapping(VALID_MAPPING, raw_dir=raw_dir)

    message = str(excinfo.value)
    assert "was not found" in message
    assert "separation_register.csv" in message


def test_present_source_files_pass(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    for cfg in VALID_MAPPING.values():
        (raw_dir / cfg["source_file"]).write_text("col\n1\n", encoding="utf-8")

    validate_mapping(VALID_MAPPING, raw_dir=raw_dir)


# --------------------------------------------------------------------------
# Shipped templates and examples must satisfy the contract they document
# --------------------------------------------------------------------------

@pytest.mark.parametrize("template_path", TEMPLATE_PATHS, ids=lambda p: p.parent.name)
def test_shipped_template_satisfies_the_contract(template_path):
    mapping = yaml.safe_load(template_path.read_text(encoding="utf-8"))

    validate_mapping(mapping, raw_dir=None, mapping_path=template_path)


def test_template_copies_are_kept_in_sync():
    contents = {p.read_text(encoding="utf-8") for p in TEMPLATE_PATHS}

    assert len(contents) == 1, (
        "The mapping templates have drifted. Keep "
        f"{[str(p) for p in TEMPLATE_PATHS]} identical."
    )


def test_adp_example_satisfies_the_contract():
    mapping = yaml.safe_load(ADP_EXAMPLE_PATH.read_text(encoding="utf-8"))

    validate_mapping(mapping, raw_dir=None, mapping_path=ADP_EXAMPLE_PATH)


SUPPORTED_PILOT_MAPPING_PATHS = [
    REPO_ROOT
    / "data"
    / "clients"
    / "CLT_KAGGLE_TEST"
    / pilot
    / "config"
    / "column_mapping.yaml"
    for pilot in (
        "PILOT_002_2026_04_02",
        "PILOT_003_2026_04_02",
        "PILOT_004_CONTROLLED_CLEAN",
        "PILOT_004_CONTROLLED_CLEAN_FULL",
    )
]


def test_supported_pilot_mappings_satisfy_the_contract():
    failures = []
    for path in SUPPORTED_PILOT_MAPPING_PATHS:
        assert path.is_file(), f"supported pilot mapping is missing: {path}"
        mapping = yaml.safe_load(path.read_text(encoding="utf-8"))
        try:
            validate_mapping(mapping, raw_dir=None, mapping_path=path)
        except MappingContractError as exc:
            failures.append(f"{path}: {exc}")

    assert not failures, "\n".join(failures)
