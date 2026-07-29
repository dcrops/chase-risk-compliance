# Running the Tests

## Default offline suite

```bash
python -m pytest
```

Collects and runs every supported test with no network access and no external
credentials. This is the command to run before committing and the one a reviewer
should be able to run on a fresh checkout.

Configuration lives in `pytest.ini`:

- `pythonpath = src`, so tests import modules unprefixed (`rkeg.detectors.pay`)
- `testpaths = tests`
- `addopts = -m "not network"`, which deselects the network-dependent tests

`tests/conftest.py` additionally puts the repository root on `sys.path`, so tests
that need the `src.`-prefixed entry points (`src.rkeg.run`) also resolve. Both
forms work; prefer the unprefixed form for detector-level tests, matching the
surrounding tests.

## Network and integration tests

```bash
python -m pytest -m network
```

Currently one test: `tests/founder_copilot/test_retrieval.py::test_semantic_query_returns_some_results`,
which falls through to embedding search and calls the OpenAI API. It needs
outbound network access and a configured API key. Every other retrieval test
resolves from rule metadata and runs in the default suite.

Run everything, network included:

```bash
python -m pytest -m ""
```

## Markers

| Marker | Meaning |
|---|---|
| `network` | Requires outbound access to an external service. Deselected by default |

Registered in `pytest.ini`. Add a marker only for a genuine external dependency.
Do not use markers, `skip` or `xfail` to hide a failing test — a test that fails
because the code is wrong must stay visible in the default suite.

## Focused runs

```bash
python -m pytest tests/rkeg -q                       # one module
python -m pytest tests/common/test_date_parsing.py   # one file
python -m pytest -k "identity" -q                    # by name
```

## Test layout

| Directory | Covers |
|---|---|
| `tests/common` | Shared contracts: date parsing, mapping validation, finding identity, run manifest |
| `tests/ingestion` | Ingestion end to end, including a non-canonical vendor mapping |
| `tests/rkeg` | RKEG detectors, rule tier selection, finding construction |
| `tests/leave`, `tests/lsl`, `tests/term` | Module detectors |
| `tests/cross_module` | Cross-module rules and finding identity |
| `tests/founder_copilot` | Rule retrieval |
| `tests/fixtures` | Sample source files, e.g. `tests/fixtures/adp` |

`tests/rkeg/conftest.py` provides fixtures that load the production rule
configuration and the `data/sample` datasets, so rule-liveness tests exercise the
shipping dispatch path rather than a parallel harness.

Tests use `tmp_path` for anything they write. No test writes into
`data/clients/`, and no test requires real client payroll data.

## Related

- `docs/contracts/ingestion_mapping_contract.md`
- `docs/contracts/finding_identity_contract.md`
- `docs/operations/run_provenance.md`
