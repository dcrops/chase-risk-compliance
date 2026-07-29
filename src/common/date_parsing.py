"""Explicit date-format handling for ingestion.

Business dates are parsed against declared formats only. Pandas format
inference is never used, because it resolves ambiguous Australian dates such as
``01/02/2024`` month-first and can silently null out valid ISO values when a
column mixes formats.

The contract is:

* ISO ``%Y-%m-%d`` is the default when a mapping declares nothing, which is what
  every existing pilot extract already supplies.
* A mapping may declare a different format for a whole run, for one dataset, or
  for one canonical column. The most specific declaration wins.
* A column may declare several formats. Each value is parsed against them in
  order, so mixed formats are supported only where they are declared.
* Blank and null values stay null. Any non-null value that no declared format
  accepts raises ``DateParsingError`` naming the dataset, column, declared
  formats and representative offending values.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping, Sequence

import pandas as pd

#: Used when a mapping declares no format. Every committed pilot extract
#: supplies ISO dates, so this preserves existing ingestion behaviour while
#: removing reliance on inference.
DEFAULT_DATE_FORMATS: tuple[str, ...] = ("%Y-%m-%d",)

#: Canonical on-disk representation. Unchanged from the original implementation.
CANONICAL_DATE_FORMAT = "%Y-%m-%d"

MAX_REPORTED_INVALID_VALUES = 5


class DateParsingError(ValueError):
    """Raised when a non-null source value does not match any declared format."""


class DateFormatConfigError(ValueError):
    """Raised when a mapping declares a date format configuration we cannot use."""


def _as_format_list(value: Any, where: str) -> list[str]:
    if isinstance(value, str):
        candidates: Sequence[Any] = [value]
    elif isinstance(value, (list, tuple)):
        candidates = value
    else:
        raise DateFormatConfigError(
            f"{where}: a date format must be a string or a list of strings, got "
            f"{type(value).__name__}."
        )

    formats: list[str] = []
    for candidate in candidates:
        if not isinstance(candidate, str) or not candidate.strip():
            raise DateFormatConfigError(
                f"{where}: date formats must be non-empty strings, got {candidate!r}."
            )
        if "%" not in candidate:
            raise DateFormatConfigError(
                f"{where}: {candidate!r} is not a strptime format. Use directives "
                f"such as %d/%m/%Y or %Y-%m-%d."
            )
        formats.append(candidate.strip())

    if not formats:
        raise DateFormatConfigError(f"{where}: no date formats were declared.")

    return formats


def resolve_date_formats(
    mapping: Mapping[str, Any] | None,
    dataset_name: str,
    column_name: str,
) -> list[str]:
    """Resolve the declared formats for one canonical date column.

    Precedence, most specific first:

    1. ``<dataset>.date_formats.<column>``
    2. ``<dataset>.date_format``
    3. top-level ``date_format``
    4. :data:`DEFAULT_DATE_FORMATS`
    """
    mapping = mapping or {}

    dataset_cfg = mapping.get(dataset_name) or {}
    if not isinstance(dataset_cfg, Mapping):
        dataset_cfg = {}

    column_formats = dataset_cfg.get("date_formats")
    if column_formats is not None:
        if not isinstance(column_formats, Mapping):
            raise DateFormatConfigError(
                f"{dataset_name}.date_formats: must be a mapping of canonical "
                f"column name to date format, got {type(column_formats).__name__}."
            )
        if column_name in column_formats:
            return _as_format_list(
                column_formats[column_name],
                f"{dataset_name}.date_formats.{column_name}",
            )

    if "date_format" in dataset_cfg:
        return _as_format_list(
            dataset_cfg["date_format"], f"{dataset_name}.date_format"
        )

    if "date_format" in mapping:
        return _as_format_list(mapping["date_format"], "date_format")

    return list(DEFAULT_DATE_FORMATS)


def _blank_to_na(series: pd.Series) -> pd.Series:
    return series.replace(r"^\s*$", pd.NA, regex=True)


def parse_date_series(
    series: pd.Series,
    dataset_name: str,
    column_name: str,
    formats: Iterable[str],
    *,
    required: bool = False,
) -> pd.Series:
    """Parse a date column against declared formats and return canonical strings.

    Args:
        required: when True, a column whose values are all null raises instead
            of returning an empty column. Callers use this for dates the
            canonical model treats as mandatory.

    Raises:
        DateParsingError: when any non-null value matches none of the formats,
            or when ``required`` is set and no value could be parsed.
    """
    formats = list(formats)
    if not formats:
        raise DateFormatConfigError(
            f"{dataset_name}.{column_name}: no date formats were declared."
        )

    original = _blank_to_na(series)
    parsed = pd.Series(pd.NaT, index=original.index, dtype="datetime64[ns]")

    outstanding = original.notna()

    for fmt in formats:
        if not outstanding.any():
            break
        attempt = pd.to_datetime(
            original[outstanding], format=fmt, errors="coerce"
        )
        parsed.loc[outstanding] = parsed.loc[outstanding].fillna(attempt)
        outstanding = original.notna() & parsed.isna()

    non_null_count = int(original.notna().sum())

    if outstanding.any():
        offending = (
            original[outstanding].astype("string").dropna().unique().tolist()
        )
        sample = offending[:MAX_REPORTED_INVALID_VALUES]
        remainder = len(offending) - len(sample)
        sample_text = ", ".join(repr(v) for v in sample)
        if remainder > 0:
            sample_text += f", and {remainder} further distinct value(s)"

        raise DateParsingError(
            f"{dataset_name}: {int(outstanding.sum())} of {non_null_count} "
            f"non-null value(s) in column '{column_name}' do not match the "
            f"declared date format(s) {formats}. Offending values: {sample_text}. "
            f"Declare the correct format for {dataset_name}.{column_name} in the "
            f"column mapping, or correct the source data."
        )

    if required and non_null_count == 0:
        raise DateParsingError(
            f"{dataset_name}: column '{column_name}' is required but contains no "
            f"date values."
        )

    return parsed.dt.strftime(CANONICAL_DATE_FORMAT)
