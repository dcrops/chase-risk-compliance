# Finding Identity Contract (v1)

One deterministic identity rule for every diagnostic module: LEAVE, LSL, TERM,
RKEG and Cross-Module Integrity.

Implemented by `src/common/finding_identity.py`. Every module's
`compute_finding_id` delegates to it.

---

## 1. Identity inputs

A `finding_id` is the first 12 hex characters of a SHA-1 digest over:

1. **rule code** — e.g. `RKEG-SUP-001`, `CM-017`
2. **primary keys** — the stable business keys in the finding's evidence, sorted
   by key name so declaration order cannot change the ID
3. **discriminator** — optional, only where one entity can legitimately produce
   several distinct findings for the same rule

Canonical form is compact JSON with sorted keys and stable separators:

```json
{"discriminator":"earnings=3420.00|super=376.20","primary_keys":{"employee_id":"W001","pay_date":"2024-02-15"},"rule_code":"RKEG-SUP-001"}
```

JSON encoding makes key/value boundaries unambiguous even when values contain
characters such as `|` or `=`. Values are normalised before hashing: booleans
become `true`/`false`, whole floats lose their trailing `.0`, and strings are
stripped. A supplied key is required to have a usable value: `None`, NaN,
infinity and blank strings raise `FindingIdentityError`. Optional keys must be
omitted rather than supplied with an empty value.

Identity is **never** derived from run timestamps, random values, or — except as
the documented last resort in section 4 — row positions.

---

## 2. Required evidence

Two entry points:

- `compute_finding_id(rule_code, primary_keys, discriminator=None)` — for
  detectors that build findings directly, such as RKEG via
  `rkeg.models.build_finding`.
- `compute_finding_id_from_evidence(rule_code, evidence_json, ...)` — for modules
  whose evidence is a JSON payload. The payload must be a JSON object containing
  a `primary_keys` object.

```json
{
  "sources": ["leave_ledger.csv"],
  "primary_keys": {
    "employee_id": "E001",
    "leave_type": "ANNUAL",
    "event_date": "2024-03-11"
  },
  "values": { "units": -7.6 },
  "explanation": "Duplicate ledger event detected."
}
```

### Failure, not fallback

`FindingIdentityError` is raised when identity evidence is missing or unusable:

- no rule code
- `primary_keys` absent or not a mapping
- a supplied primary-key name or value that is null, NaN, non-finite, or blank
- evidence that is empty, not valid JSON, or not a JSON object

There is deliberately no rule-only fallback. A rule-only ID would give every
finding for that rule the same identity, which is worse than a loud failure
because it silently collapses findings during aggregation.

### Organisation-level findings

Some findings describe the engagement rather than an entity — for example
`RKEG-GOV-001`, "no override log was supplied at all". These have no primary keys
and must opt in:

```python
compute_finding_id(rule_code, {}, allow_empty_keys=True)
```

The opt-in is required so a forgotten key mapping is never mistaken for a
deliberate organisation-level finding.

---

## 3. Choosing primary keys

Match the keys to the rule's grain.

| Rule grain | Primary keys |
|---|---|
| One finding per employee | `employee_id` |
| One finding per employee per period | `employee_id`, `pay_date` or `period_month` |
| One finding per source record | the record's natural key, e.g. `transaction_id` |
| One finding per engagement | none, with `allow_empty_keys=True` |

Where one employee can legitimately have several findings for the same rule and
the same keys, add a discriminator describing what differs (`units=-7.60`,
`earnings=3420.00|super=376.20`). A discriminator distinguishes; it does not
replace missing keys.

If a rule describes a *group* (LEAVE-008, "duplicate ledger event"), emit one
finding per group with the group size in `values.occurrence_count`, rather than
one finding per member sharing an ID.

---

## 4. Row-ordinal fallback

A few rules fire per source record on datasets that may not carry a natural key
(`RKEG-LEAVE-001`, `RKEG-SUP-005`, `LEAVE-014`). These prefer `transaction_id`
and fall back to the source row ordinal only when the extract supplies none.

Consequence, stated plainly: with the fallback in play, IDs are stable while the
input file is unchanged, but **shift if rows are reordered** even though the data
is equivalent. Supplying a stable record identifier in the extract removes the
fallback. This is the one place where identity depends on file ordering.

---

## 5. Rerun stability

Given identical inputs, rule configuration and code, a rerun produces byte
identical findings, including IDs. Verified for RKEG in
`tests/rkeg/test_rkeg_finding_construction.py` and per-rule tests; and
end to end by re-running a module twice and diffing the findings CSV.

IDs change when, and only when, the identity inputs change:

- the rule code is renamed
- a primary key value changes (a corrected employee ID, a corrected date)
- the discriminator changes
- a rule's key set is deliberately revised, as in this change set

IDs do **not** change with run time, execution mode, machine, output ordering,
or unrelated rules firing.

Because IDs are content-derived, they are comparable across pilots. Two pilots
with the same employee, rule and keys produce the same ID. Scope comparisons by
client and pilot rather than treating a `finding_id` as globally unique.

---

## 6. Collision expectations

| Situation | Expected |
|---|---|
| Same rule, same keys, rerun | Same ID |
| Same rule, different employees | Different IDs |
| Same rule and employee, different period | Different IDs |
| Same rule, employee, keys, different values | Different IDs via discriminator |
| Duplicate source records | Different IDs via natural key or row ordinal |
| Missing or malformed identity evidence | `FindingIdentityError` |

Cross-module `CM-017` and `CM-020` previously omitted `employee_id` from their
evidence, so all their findings collapsed onto one ID per rule. Both now record
their primary keys; covered by
`tests/cross_module/test_cross_module_finding_identity.py`.

`finding_id` is a primary key for a findings CSV within one pilot run. Any
duplicate is a defect, not an expected outcome.

---

## 7. Downstream assumptions

Reviewed before changing the format:

- The ID remains a 12-character lowercase hex string, so column widths, report
  templates and CSV schemas are unchanged.
- Module summaries aggregate on `rule_code`, `severity`, `classification` and
  `risk_dimension`, never on `finding_id`, so counts are unaffected.
- Cross-module aggregation concatenates module findings and does not join on
  `finding_id`.

Note for anyone holding earlier outputs: RKEG IDs were random UUIDs, so they
change wholesale under this contract. IDs for rules whose key sets were revised
also change. Do not compare `finding_id` values across the boundary of this
change set; compare on rule code plus business keys instead.

The corrective hardening follow-up also replaced the initial delimiter-joined
canonical form with canonical JSON. Therefore deterministic IDs created by the
first hardening implementation change once more, even when their logical
identity evidence is unchanged. The 12-character lowercase-hex format is
unchanged.

---

## 8. Related

- `docs/contracts/ingestion_mapping_contract.md`
- `docs/operations/run_provenance.md`
- `docs/operations/testing.md`
