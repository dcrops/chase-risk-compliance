import json
from pathlib import Path
import shutil

import pandas as pd
import pytest

from common.execution_metadata import finalize_module_run
from common.run_manifest import GIT_SHA_UNAVAILABLE
from cross_module_integrity import run as cross_module_run
from ingestion import ingest
from termination_exposure import run as term_run

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def pilot(tmp_path):
    processed = tmp_path / "processed"
    config = tmp_path / "config"
    outputs = tmp_path / "outputs"
    processed.mkdir()
    config.mkdir()
    outputs.mkdir()

    (processed / "employees.csv").write_text(
        "employee_id,start_date\nPRIVATE-E001,2024-01-01\n",
        encoding="utf-8",
    )
    (config / "rules.yml").write_text("rules: []\n", encoding="utf-8")
    return tmp_path


def _finalize(pilot: Path, module: str):
    report = pilot / "outputs" / f"{module.lower()}_findings.csv"
    report.write_text("finding_id\nabc\n", encoding="utf-8")
    return finalize_module_run(
        output_dir=pilot / "outputs",
        module_name=module,
        mode="full",
        include_supporting=False,
        client="CLT_TEST",
        pilot="PILOT_TEST",
        input_paths=[pilot / "processed" / "employees.csv"],
        config_paths=[pilot / "config" / "rules.yml"],
        output_paths=[report],
        pilot_root=pilot,
        repo_root=pilot,
    )


@pytest.mark.parametrize(
    ("module", "filename"),
    [
        ("LEAVE", "run_manifest_leave.json"),
        ("LSL", "run_manifest_lsl.json"),
        ("TERM", "run_manifest_term.json"),
        ("RKEG", "run_manifest_rkeg.json"),
        ("CROSS_MODULE", "run_manifest_cross_module.json"),
    ],
)
def test_each_diagnostic_module_gets_a_distinct_manifest(pilot, module, filename):
    metadata_path, manifest_path = _finalize(pilot, module)

    assert manifest_path.name == filename
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["module"] == module
    assert manifest["client"] == "CLT_TEST"
    assert manifest["pilot"] == "PILOT_TEST"
    assert manifest["inputs"][0]["row_count"] == 1
    assert manifest["config_combined_sha256"]
    assert "PRIVATE-E001" not in manifest_path.read_text(encoding="utf-8")

    metadata = pd.read_csv(metadata_path)
    assert metadata.loc[0, "run_manifest"] == filename
    assert metadata.loc[0, "git_commit_sha"] == manifest["git_commit_sha"]


def test_running_another_module_does_not_overwrite_existing_manifest(pilot):
    _, leave_manifest = _finalize(pilot, "LEAVE")
    leave_before = leave_manifest.read_bytes()

    _, rkeg_manifest = _finalize(pilot, "RKEG")

    assert leave_manifest.read_bytes() == leave_before
    assert rkeg_manifest.is_file()
    assert rkeg_manifest != leave_manifest


def test_module_manifest_uses_git_fallback_outside_a_checkout(pilot, monkeypatch):
    monkeypatch.delenv("CRC_GIT_SHA", raising=False)

    _, manifest_path = _finalize(pilot, "TERM")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["git_commit_sha"] == GIT_SHA_UNAVAILABLE


def test_production_orchestration_writes_linked_module_manifests(tmp_path, monkeypatch):
    pilot_root = tmp_path / "CLT_TEST" / "PILOT_ADP"
    raw_dir = pilot_root / "raw"
    config_dir = pilot_root / "config"
    raw_dir.mkdir(parents=True)
    config_dir.mkdir()
    for source in (REPO_ROOT / "tests" / "fixtures" / "adp").glob("*.csv"):
        shutil.copy(source, raw_dir / source.name)
    shutil.copy(
        REPO_ROOT / "templates" / "examples" / "adp_column_mapping_example.yaml",
        config_dir / "column_mapping.yaml",
    )

    monkeypatch.setattr(ingest, "DATA_ROOT", tmp_path)
    ingest.main("CLT_TEST", "PILOT_ADP")
    monkeypatch.setattr(term_run, "get_processed_dir", lambda *_: pilot_root / "processed")
    monkeypatch.setattr(term_run, "get_outputs_dir", lambda *_: pilot_root / "outputs")
    monkeypatch.setattr(
        cross_module_run, "get_processed_dir", lambda *_: pilot_root / "processed"
    )
    monkeypatch.setattr(
        cross_module_run, "get_outputs_dir", lambda *_: pilot_root / "outputs"
    )

    assert term_run.main("CLT_TEST", "PILOT_ADP") == 0
    assert cross_module_run.main("CLT_TEST", "PILOT_ADP") == 0

    for module, expected_name in (
        ("term", "run_manifest_term.json"),
        ("cross_module", "run_manifest_cross_module.json"),
    ):
        manifest_path = pilot_root / "outputs" / expected_name
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        metadata = pd.read_csv(
            pilot_root / "outputs" / f"{module}_execution_metadata.csv"
        )
        assert manifest["module"] == module.upper()
        assert metadata.loc[0, "run_manifest"] == expected_name
    assert (pilot_root / "outputs" / "run_manifest_ingestion.json").is_file()
