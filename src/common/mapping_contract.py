"""Validation of a pilot's column mapping, run before any dataset is read.

The active ingestion contract is:

.. code-block:: yaml

    <dataset>:
      source_file: <file name inside the pilot raw directory>
      rename:
        <source column>: <canonical column>

The rename direction is source column on the left, canonical column on the
right, because ingestion applies it directly to ``DataFrame.rename``.

An earlier template used ``source`` plus ``columns`` with the opposite
direction. That shape was never supported by ingestion, so it is rejected with
a migration message rather than silently accepted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from common.date_parsing import DateFormatConfigError, resolve_date_formats

#: Datasets ingestion requires in order to produce the canonical model.
REQUIRED_DATASETS: tuple[str, ...] = (
    "employees",
    "terminations",
    "pay_events",
    "leave_ledger",
)

#: Datasets ingestion uses when supplied and skips when absent.
OPTIONAL_DATASETS: tuple[str, ...] = ("leave_snapshot",)

KNOWN_DATASETS: tuple[str, ...] = REQUIRED_DATASETS + OPTIONAL_DATASETS

#: Keys accepted inside a dataset configuration block.
ALLOWED_DATASET_KEYS: frozenset[str] = frozenset(
    {"source_file", "rename", "date_format", "date_formats"}
)

#: Keys accepted at the top level alongside dataset blocks.
ALLOWED_TOP_LEVEL_KEYS: frozenset[str] = frozenset({"date_format"})

#: Canonical date columns per dataset, used to validate date-format declarations.
CANONICAL_DATE_COLUMNS: dict[str, tuple[str, ...]] = {
    "employees": ("start_date",),
    "terminations": ("termination_date",),
    "pay_events": ("pay_date",),
    "leave_ledger": ("event_date",),
    "leave_snapshot": ("as_of_date",),
}

STALE_FORMAT_KEYS = ("source", "columns")


class MappingContractError(ValueError):
    """Raised when a column mapping does not satisfy the ingestion contract."""


def _describe(mapping_path: Path | None) -> str:
    return str(mapping_path) if mapping_path else "column mapping"


def _validate_dataset(
    dataset_name: str,
    cfg: Any,
    mapping: Mapping[str, Any],
    raw_dir: Path | None,
    problems: list[str],
) -> None:
    if not isinstance(cfg, Mapping):
        problems.append(
            f"{dataset_name}: expected a configuration block with source_file and "
            f"rename, got {type(cfg).__name__}."
        )
        return

    stale_keys = [key for key in STALE_FORMAT_KEYS if key in cfg]
    if stale_keys:
        problems.append(
            f"{dataset_name}: uses the withdrawn template keys {stale_keys}. The "
            f"supported contract is 'source_file' plus 'rename', where rename maps "
            f"source column (left) to canonical column (right). The withdrawn "
            f"'source'/'columns' shape used the opposite direction and was never "
            f"read by ingestion, so it cannot be accepted as-is."
        )
        return

    unknown_keys = sorted(set(cfg) - ALLOWED_DATASET_KEYS)
    if unknown_keys:
        problems.append(
            f"{dataset_name}: unsupported configuration key(s) {unknown_keys}. "
            f"Supported keys are {sorted(ALLOWED_DATASET_KEYS)}."
        )

    source_file = cfg.get("source_file")
    if source_file is None:
        problems.append(f"{dataset_name}: 'source_file' is missing.")
    elif not isinstance(source_file, str) or not source_file.strip():
        problems.append(
            f"{dataset_name}: 'source_file' must be a non-empty file name, got "
            f"{source_file!r}."
        )
    elif raw_dir is not None and not (raw_dir / source_file).exists():
        problems.append(
            f"{dataset_name}: source file '{source_file}' was not found in {raw_dir}."
        )

    if "rename" not in cfg:
        problems.append(
            f"{dataset_name}: 'rename' is missing. Declare it as "
            f"'<source column>: <canonical column>' even when the source headers "
            f"are already canonical."
        )
    else:
        rename = cfg.get("rename")
        if not isinstance(rename, Mapping):
            problems.append(
                f"{dataset_name}: 'rename' must be a mapping of source column to "
                f"canonical column, got {type(rename).__name__}."
            )
        elif not rename:
            problems.append(f"{dataset_name}: 'rename' is empty.")
        else:
            for source_col, canonical_col in rename.items():
                if not isinstance(source_col, str) or not str(source_col).strip():
                    problems.append(
                        f"{dataset_name}.rename: source column names must be "
                        f"non-empty strings, got {source_col!r}."
                    )
                if not isinstance(canonical_col, str) or not str(canonical_col).strip():
                    problems.append(
                        f"{dataset_name}.rename: canonical column names must be "
                        f"non-empty strings, got {canonical_col!r} for source "
                        f"column {source_col!r}."
                    )

            canonical_targets = [
                c for c in rename.values() if isinstance(c, str)
            ]
            duplicates = sorted(
                {c for c in canonical_targets if canonical_targets.count(c) > 1}
            )
            if duplicates:
                problems.append(
                    f"{dataset_name}.rename: canonical column(s) {duplicates} are "
                    f"mapped from more than one source column, so the resulting "
                    f"canonical column would be ambiguous."
                )

    date_formats = cfg.get("date_formats")
    if date_formats is not None and isinstance(date_formats, Mapping):
        known_date_columns = CANONICAL_DATE_COLUMNS.get(dataset_name, ())
        for column in date_formats:
            if column not in known_date_columns:
                problems.append(
                    f"{dataset_name}.date_formats: '{column}' is not a canonical "
                    f"date column for this dataset. Canonical date column(s): "
                    f"{list(known_date_columns)}."
                )

    for column in CANONICAL_DATE_COLUMNS.get(dataset_name, ()):
        try:
            resolve_date_formats(mapping, dataset_name, column)
        except DateFormatConfigError as exc:
            problems.append(str(exc))


def validate_mapping(
    mapping: Any,
    raw_dir: Path | None = None,
    mapping_path: Path | None = None,
) -> None:
    """Validate a loaded column mapping.

    Args:
        mapping: the parsed YAML mapping.
        raw_dir: when supplied, referenced source files must exist inside it.
        mapping_path: used only to make error messages actionable.

    Raises:
        MappingContractError: listing every problem found, so a client mapping
            can be corrected in one pass rather than one error at a time.
    """
    if mapping is None:
        raise MappingContractError(
            f"{_describe(mapping_path)} is empty. It must declare the datasets "
            f"{list(REQUIRED_DATASETS)}."
        )

    if not isinstance(mapping, Mapping):
        raise MappingContractError(
            f"{_describe(mapping_path)} must be a mapping of dataset name to "
            f"configuration, got {type(mapping).__name__}."
        )

    problems: list[str] = []

    unknown_top_level = sorted(
        key for key in mapping if key not in KNOWN_DATASETS and key not in ALLOWED_TOP_LEVEL_KEYS
    )
    if unknown_top_level:
        problems.append(
            f"unrecognised top-level key(s) {unknown_top_level}. Recognised "
            f"datasets are {list(KNOWN_DATASETS)}; recognised settings are "
            f"{sorted(ALLOWED_TOP_LEVEL_KEYS)}."
        )

    for dataset_name in REQUIRED_DATASETS:
        if dataset_name not in mapping:
            problems.append(
                f"{dataset_name}: required dataset is not declared in the mapping."
            )

    for dataset_name in KNOWN_DATASETS:
        if dataset_name in mapping:
            _validate_dataset(
                dataset_name, mapping[dataset_name], mapping, raw_dir, problems
            )

    if "date_format" in mapping:
        try:
            resolve_date_formats({"date_format": mapping["date_format"]}, "unused", "unused")
        except DateFormatConfigError as exc:
            problems.append(str(exc))

    if problems:
        bullets = "\n".join(f"  - {problem}" for problem in problems)
        raise MappingContractError(
            f"{_describe(mapping_path)} does not satisfy the ingestion contract:\n"
            f"{bullets}"
        )
