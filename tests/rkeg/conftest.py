"""Shared helpers for RKEG tests that run rules against the sample dataset.

These replace the retired ``rkeg.engine.run_rkeg_engine`` entry point. Rules are
now loaded from the production rule configuration and dispatched through
``rkeg.detectors.registry``, which is the path ``rkeg.run.main`` uses, so these
tests exercise the shipping code rather than a parallel test harness.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

from rkeg.datasets import load_all_datasets
from rkeg.detectors.registry import run_rule as dispatch_rule
from rkeg.models import Finding

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DATA_DIR = REPO_ROOT / "data" / "sample"
RKEG_RULES_PATH = REPO_ROOT / "src" / "rkeg" / "config" / "rkeg_rules.yml"

#: Tiers ``rkeg.run.main`` executes. Kept here so tier-scoped tests and
#: production selection cannot drift apart silently.
PRODUCTION_TIERS = frozenset({1, 2})


def load_rkeg_rules() -> list[dict]:
    payload = yaml.safe_load(RKEG_RULES_PATH.read_text(encoding="utf-8")) or {}
    return payload.get("rules", []) or []


def get_rule(rule_id: str) -> dict:
    for rule in load_rkeg_rules():
        if str(rule.get("id", "")).strip() == rule_id:
            return rule
    raise AssertionError(
        f"{rule_id} is not declared in {RKEG_RULES_PATH.name}. If the rule was "
        f"intentionally retired, remove the test rather than weakening it."
    )


@pytest.fixture(scope="session")
def rkeg_rules() -> list[dict]:
    """Every rule declared in the production RKEG rule configuration."""
    return load_rkeg_rules()


@pytest.fixture
def rkeg_rule():
    """Look up one configured rule by ID, failing if it has been retired."""
    return get_rule


@pytest.fixture(scope="session")
def sample_datasets() -> dict[str, pd.DataFrame]:
    """Sample datasets, normalised the way ``rkeg.run.main`` normalises them."""
    assert SAMPLE_DATA_DIR.is_dir(), f"Sample data directory missing: {SAMPLE_DATA_DIR}"

    datasets = load_all_datasets(SAMPLE_DATA_DIR)
    for df in datasets.values():
        if not df.empty and "employee_id" in df.columns:
            df["employee_id"] = df["employee_id"].astype(str).str.strip()
    return datasets


@pytest.fixture
def run_sample_rule(sample_datasets):
    """Run one configured rule against the sample datasets via the registry."""

    def _run(rule_id: str) -> list[Finding]:
        rule = get_rule(rule_id)
        assert int(rule.get("tier", 1)) in PRODUCTION_TIERS, (
            f"{rule_id} is tier {rule.get('tier')}, which "
            f"rkeg.run.main does not execute."
        )
        return list(dispatch_rule(rule, sample_datasets, context={}))

    return _run
