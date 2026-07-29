"""Deterministic finding identity for all diagnostic modules.

A finding's identity is derived from:

* the rule code;
* the stable primary keys recorded in the finding's evidence;
* an optional discriminator, used where one entity can legitimately produce
  several distinct findings for the same rule.

Identity is never derived from run timestamps or random values. A small number
of source-record rules use a documented row-ordinal fallback when no natural
record identifier exists, so those IDs remain stable only while source ordering
is unchanged.

Findings that describe the whole engagement rather than an entity (for example
"no override log was supplied at all") have no primary keys. Those callers must
opt in with ``allow_empty_keys=True`` so that a missing key mapping is never
mistaken for a deliberate organisation-level finding.
"""

from __future__ import annotations

import hashlib
import json
import math
from numbers import Real
from typing import Any, Mapping, Optional

ID_LENGTH = 12


class FindingIdentityError(ValueError):
    """Raised when a finding cannot be given a trustworthy identity."""


def _normalise_value(value: Any, label: str) -> str:
    if value is None or type(value).__name__ in {"NAType", "NaTType"}:
        raise FindingIdentityError(f"{label} cannot be null.")
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Real):
        numeric = float(value)
        if not math.isfinite(numeric):
            raise FindingIdentityError(f"{label} must be finite, got {value!r}.")
        if numeric.is_integer():
            return str(int(numeric))
    is_nan = getattr(value, "is_nan", None)
    if callable(is_nan) and is_nan():
        raise FindingIdentityError(f"{label} cannot be NaN.")

    normalised = str(value).strip()
    if not normalised:
        raise FindingIdentityError(f"{label} cannot be blank.")
    return normalised


def is_usable_key_value(value: Any) -> bool:
    """Whether a value can be hashed as a primary key without raising."""
    try:
        _normalise_value(value, "probe")
    except FindingIdentityError:
        return False
    return True


def drop_unusable_keys(primary_keys: Mapping[str, Any]) -> dict[str, Any]:
    """Return primary keys with unusable values removed.

    The contract requires optional keys to be omitted rather than supplied with
    an empty value. Detectors that report on records with a missing or
    unparseable date use this so that the absent value narrows the key set
    instead of raising ``FindingIdentityError`` on exactly the malformed data
    the rule exists to surface. An empty result still fails in
    ``compute_finding_id``, so a wholly unidentifiable finding remains loud.
    """
    return {
        key: value
        for key, value in primary_keys.items()
        if is_usable_key_value(value)
    }


def canonical_identity(
    rule_code: str,
    primary_keys: Mapping[str, Any],
    discriminator: Optional[str] = None,
) -> str:
    """Return unambiguous canonical JSON used as the identity hash input."""
    normalised_keys: dict[str, str] = {}
    for key, value in primary_keys.items():
        if not isinstance(key, str) or not key.strip():
            raise FindingIdentityError(
                f"{rule_code}: primary key names must be non-blank strings, got {key!r}."
            )
        normalised_keys[key.strip()] = _normalise_value(
            value, f"{rule_code}: primary key '{key.strip()}'"
        )

    payload: dict[str, Any] = {
        "primary_keys": normalised_keys,
        "rule_code": str(rule_code).strip(),
    }
    if discriminator is not None:
        payload["discriminator"] = _normalise_value(
            discriminator, f"{rule_code}: discriminator"
        )
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def compute_finding_id(
    rule_code: str,
    primary_keys: Mapping[str, Any],
    discriminator: Optional[str] = None,
    *,
    allow_empty_keys: bool = False,
) -> str:
    """Compute a deterministic finding ID, or fail loudly.

    Raises:
        FindingIdentityError: when the rule code is missing, when
            ``primary_keys`` is not a mapping, when a supplied key or value is
            null, NaN or blank, or when no primary keys are supplied without
            declaring an organisation-level finding.
    """
    if not rule_code or not str(rule_code).strip():
        raise FindingIdentityError(
            "Cannot compute a finding ID without a rule code."
        )

    if not isinstance(primary_keys, Mapping):
        raise FindingIdentityError(
            f"{rule_code}: primary_keys must be a mapping of key name to value, "
            f"got {type(primary_keys).__name__}."
        )

    if not primary_keys and not allow_empty_keys:
        raise FindingIdentityError(
            f"{rule_code}: no primary keys were supplied. A finding cannot be "
            f"identified by rule code alone, because that would collapse "
            f"distinct findings onto one ID. Supply the evidence primary keys, "
            f"or pass allow_empty_keys=True for an organisation-level finding."
        )

    canonical = canonical_identity(rule_code, primary_keys, discriminator)
    return hashlib.sha1(canonical.encode("utf-8")).hexdigest()[:ID_LENGTH]


def compute_finding_id_from_evidence(
    rule_code: str,
    evidence_json: Optional[str],
    discriminator: Optional[str] = None,
    *,
    allow_empty_keys: bool = False,
) -> str:
    """Compute a finding ID from a JSON evidence payload.

    The payload must be valid JSON containing a ``primary_keys`` mapping.
    Malformed evidence fails rather than silently falling back to a rule-only
    identity shared by every finding for that rule.
    """
    if evidence_json is None or not str(evidence_json).strip():
        raise FindingIdentityError(
            f"{rule_code}: evidence is empty, so the finding has no identity "
            f"evidence to hash."
        )

    try:
        payload = json.loads(evidence_json)
    except (TypeError, ValueError) as exc:
        raise FindingIdentityError(
            f"{rule_code}: evidence is not valid JSON, so primary keys cannot "
            f"be read for finding identity ({exc})."
        ) from exc

    if not isinstance(payload, dict):
        raise FindingIdentityError(
            f"{rule_code}: evidence must be a JSON object containing "
            f"primary_keys, got {type(payload).__name__}."
        )

    if "primary_keys" not in payload:
        raise FindingIdentityError(
            f"{rule_code}: evidence has no primary_keys entry. Add the stable "
            f"identifying keys for this finding, or pass allow_empty_keys=True "
            f"for an organisation-level finding."
        )

    primary_keys = payload.get("primary_keys")
    if primary_keys is None:
        primary_keys = {}

    if not isinstance(primary_keys, Mapping):
        raise FindingIdentityError(
            f"{rule_code}: evidence primary_keys must be a JSON object, got "
            f"{type(primary_keys).__name__}."
        )

    return compute_finding_id(
        rule_code,
        primary_keys,
        discriminator,
        allow_empty_keys=allow_empty_keys,
    )
