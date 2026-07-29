import hashlib
import json
import platform

import pytest

from common import run_manifest
from common.run_manifest import (
    GIT_SHA_UNAVAILABLE,
    add_outputs,
    build_manifest,
    combined_digest,
    count_csv_rows,
    dependency_versions,
    discover_git_sha,
    hash_file,
    manifest_filename,
    read_manifest,
    write_manifest,
)


@pytest.fixture
def pilot(tmp_path):
    raw = tmp_path / "raw"
    config = tmp_path / "config"
    outputs = tmp_path / "outputs"
    raw.mkdir()
    config.mkdir()
    outputs.mkdir()

    (raw / "employees.csv").write_text(
        "employee_id,start_date\nE001,2024-02-01\nE002,2024-03-02\n", encoding="utf-8"
    )
    (raw / "pay_events.csv").write_text(
        "employee_id,pay_date\nE001,2024-02-15\n", encoding="utf-8"
    )
    (config / "column_mapping.yaml").write_text("employees: {}\n", encoding="utf-8")

    return tmp_path


# --------------------------------------------------------------------------
# Hashing and row counting
# --------------------------------------------------------------------------

def test_hash_file_matches_sha256_of_contents(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_bytes(b"payroll")

    assert hash_file(path) == hashlib.sha256(b"payroll").hexdigest()


def test_hash_file_is_stable_for_identical_contents(tmp_path):
    first = tmp_path / "a.csv"
    second = tmp_path / "b.csv"
    first.write_text("x\n1\n", encoding="utf-8")
    second.write_text("x\n1\n", encoding="utf-8")

    assert hash_file(first) == hash_file(second)


def test_hash_file_changes_when_contents_change(tmp_path):
    path = tmp_path / "a.csv"
    path.write_text("x\n1\n", encoding="utf-8")
    before = hash_file(path)
    path.write_text("x\n2\n", encoding="utf-8")

    assert hash_file(path) != before


def test_combined_digest_is_order_independent():
    assert combined_digest(["a", "b"]) == combined_digest(["b", "a"])


def test_combined_digest_changes_when_any_hash_changes():
    assert combined_digest(["a", "b"]) != combined_digest(["a", "c"])


def test_row_count_excludes_the_header(pilot):
    assert count_csv_rows(pilot / "raw" / "employees.csv") == 2
    assert count_csv_rows(pilot / "raw" / "pay_events.csv") == 1


def test_row_count_is_none_for_non_csv_files(pilot):
    assert count_csv_rows(pilot / "config" / "column_mapping.yaml") is None


# --------------------------------------------------------------------------
# Manifest content
# --------------------------------------------------------------------------

def test_manifest_records_run_identity_and_environment(pilot):
    manifest = build_manifest(
        client="CLT_TEST",
        pilot="PILOT_TEST",
        execution_mode="full",
        module="RKEG",
        input_paths=[pilot / "raw" / "employees.csv"],
        config_paths=[pilot / "config" / "column_mapping.yaml"],
        relative_to=pilot,
    )

    assert manifest.run_id
    assert manifest.generated_at_utc.endswith("+00:00")
    assert manifest.client == "CLT_TEST"
    assert manifest.pilot == "PILOT_TEST"
    assert manifest.execution_mode == "full"
    assert manifest.module == "RKEG"
    assert manifest.python_version == platform.python_version()
    assert manifest.git_commit_sha


def test_manifest_records_input_hashes_and_row_counts(pilot):
    manifest = build_manifest(
        input_paths=[
            pilot / "raw" / "employees.csv",
            pilot / "raw" / "pay_events.csv",
        ],
        relative_to=pilot,
    )

    by_path = {record.path: record for record in manifest.inputs}

    assert set(by_path) == {"raw/employees.csv", "raw/pay_events.csv"}
    assert by_path["raw/employees.csv"].row_count == 2
    assert by_path["raw/employees.csv"].sha256 == hash_file(pilot / "raw" / "employees.csv")
    assert by_path["raw/employees.csv"].size_bytes > 0
    assert manifest.inputs_combined_sha256


def test_manifest_records_config_hashes_and_a_combined_digest(pilot):
    manifest = build_manifest(
        config_paths=[pilot / "config" / "column_mapping.yaml"],
        relative_to=pilot,
    )

    assert len(manifest.config_files) == 1
    assert manifest.config_combined_sha256 == combined_digest(
        [manifest.config_files[0].sha256]
    )


def test_manifest_records_key_dependency_versions():
    versions = dependency_versions()

    assert "pandas" in versions
    assert versions["pandas"] != ""


def test_manifest_skips_missing_input_files(pilot):
    manifest = build_manifest(
        input_paths=[pilot / "raw" / "employees.csv", pilot / "raw" / "absent.csv"],
        relative_to=pilot,
    )

    assert [r.path for r in manifest.inputs] == ["raw/employees.csv"]


def test_manifest_carries_no_record_level_data(pilot):
    manifest = build_manifest(
        input_paths=[pilot / "raw" / "employees.csv"],
        relative_to=pilot,
    )

    payload = json.dumps(manifest.to_dict())

    assert "E001" not in payload
    assert "2024-02-01" not in payload


def test_input_hashes_are_stable_across_repeated_builds(pilot):
    first = build_manifest(input_paths=[pilot / "raw" / "employees.csv"], relative_to=pilot)
    second = build_manifest(input_paths=[pilot / "raw" / "employees.csv"], relative_to=pilot)

    assert first.inputs_combined_sha256 == second.inputs_combined_sha256
    assert first.run_id != second.run_id


def test_input_digest_changes_when_an_input_changes(pilot):
    before = build_manifest(input_paths=[pilot / "raw" / "employees.csv"], relative_to=pilot)

    (pilot / "raw" / "employees.csv").write_text(
        "employee_id,start_date\nE001,2024-02-01\n", encoding="utf-8"
    )
    after = build_manifest(input_paths=[pilot / "raw" / "employees.csv"], relative_to=pilot)

    assert before.inputs_combined_sha256 != after.inputs_combined_sha256


# --------------------------------------------------------------------------
# Git SHA fallback
# --------------------------------------------------------------------------

def test_git_sha_is_read_from_the_environment_when_provided(monkeypatch):
    monkeypatch.setenv("CRC_GIT_SHA", "abc123")

    assert discover_git_sha() == "abc123"


def test_missing_git_metadata_records_the_documented_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("CRC_GIT_SHA", raising=False)

    assert discover_git_sha(repo_root=tmp_path) == GIT_SHA_UNAVAILABLE


def test_git_binary_absent_does_not_crash_a_packaged_run(monkeypatch):
    monkeypatch.delenv("CRC_GIT_SHA", raising=False)

    def explode(*args, **kwargs):
        raise FileNotFoundError("git is not installed")

    monkeypatch.setattr(run_manifest.subprocess, "run", explode)

    assert discover_git_sha() == GIT_SHA_UNAVAILABLE


def test_manifest_build_succeeds_without_git(monkeypatch, pilot):
    monkeypatch.delenv("CRC_GIT_SHA", raising=False)
    monkeypatch.setattr(run_manifest, "discover_git_sha", lambda *a, **k: GIT_SHA_UNAVAILABLE)

    manifest = build_manifest(input_paths=[pilot / "raw" / "employees.csv"], relative_to=pilot)

    assert manifest.git_commit_sha == GIT_SHA_UNAVAILABLE


# --------------------------------------------------------------------------
# Outputs and writing
# --------------------------------------------------------------------------

def test_outputs_are_recorded_when_supplied(pilot):
    report = pilot / "outputs" / "rkeg_findings.csv"
    report.write_text("finding_id\nabc\n", encoding="utf-8")

    manifest = add_outputs(
        build_manifest(relative_to=pilot, config_paths=[pilot / "config" / "column_mapping.yaml"]),
        [report],
        relative_to=pilot,
    )

    assert [r.path for r in manifest.outputs] == ["outputs/rkeg_findings.csv"]
    assert manifest.outputs_combined_sha256


def test_manifest_is_written_as_json_into_the_outputs_directory(pilot):
    manifest = build_manifest(
        client="CLT_TEST",
        pilot="PILOT_TEST",
        input_paths=[pilot / "raw" / "employees.csv"],
        relative_to=pilot,
    )

    filename = manifest_filename("RKEG")
    path = write_manifest(manifest, pilot / "outputs", filename=filename)

    assert path.name == "run_manifest_rkeg.json"
    assert path.parent == pilot / "outputs"

    payload = read_manifest(pilot / "outputs", filename)
    assert payload["client"] == "CLT_TEST"
    assert payload["manifest_version"]
    assert payload["inputs"][0]["path"] == "raw/employees.csv"


def test_manifest_creates_the_outputs_directory_when_absent(tmp_path):
    manifest = build_manifest(module="INGESTION")

    path = write_manifest(manifest, tmp_path / "new_outputs")

    assert path.exists()
    assert path.name == "run_manifest_ingestion.json"


def test_manifest_filenames_are_module_specific():
    assert manifest_filename("INGESTION") == "run_manifest_ingestion.json"
    assert manifest_filename("CROSS_MODULE") == "run_manifest_cross_module.json"


def test_manifest_notes_document_the_initial_limitations():
    manifest = build_manifest()

    joined = " ".join(manifest.notes)
    assert "no payroll records" in joined
    assert "Output hashing" in joined
