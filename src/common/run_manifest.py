"""Minimal run manifest so a completed run can be reproduced and evidenced.

This is a bounded first version, not a provenance subsystem. It records what a
run consumed and what code and configuration produced it:

* run identity and timing;
* client and pilot identifiers, and execution mode;
* every input file with its size, SHA-256 hash and row count;
* every rule or configuration file with its SHA-256 hash, plus a combined digest;
* the Git commit SHA where discoverable, the Python version and key dependency
  versions.

Deliberate limitations:

* Output hashing is opt-in via :func:`add_outputs`. Production orchestration
  supplies the outputs it can identify exactly; complete report-package coverage
  remains deferred.
* The manifest records file digests and row counts only. It never records
  payroll records, employee identifiers or other personal information.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Any, Iterable, Sequence

MANIFEST_VERSION = "1.0"

#: Recorded because they materially affect diagnostic output.
TRACKED_DEPENDENCIES: tuple[str, ...] = (
    "pandas",
    "numpy",
    "pyyaml",
    "jinja2",
    "weasyprint",
    "markdown",
)

#: Recorded when a Git SHA cannot be discovered, for example in a packaged or
#: exported run. A missing SHA must never fail a legitimate run.
GIT_SHA_UNAVAILABLE = "unavailable"

HASH_CHUNK_BYTES = 1 << 20


def manifest_filename(module_name: str) -> str:
    """Return the stable, module-specific manifest filename."""
    normalised = str(module_name).strip().lower().replace("-", "_").replace(" ", "_")
    if not normalised:
        raise ValueError("A module name is required to build a manifest filename.")
    return f"run_manifest_{normalised}.json"


def hash_file(path: Path) -> str:
    """Return the SHA-256 hex digest of a file, read in chunks."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(HASH_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def combined_digest(hashes: Iterable[str]) -> str:
    """Return an order-independent digest over a collection of file hashes."""
    joined = "|".join(sorted(h for h in hashes if h))
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def count_csv_rows(path: Path) -> int | None:
    """Count data rows in a CSV, excluding the header. None when not a CSV."""
    if path.suffix.lower() != ".csv":
        return None
    with open(path, "r", encoding="utf-8", errors="replace", newline="") as handle:
        total = sum(1 for _ in handle)
    return max(total - 1, 0)


def discover_git_sha(repo_root: Path | None = None) -> str:
    """Return the current Git commit SHA, or :data:`GIT_SHA_UNAVAILABLE`.

    Packaged and exported runs have no Git metadata, so every failure mode
    resolves to the documented fallback rather than raising.
    """
    env_sha = os.environ.get("CRC_GIT_SHA")
    if env_sha and env_sha.strip():
        return env_sha.strip()

    cwd = str(repo_root) if repo_root else None

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return GIT_SHA_UNAVAILABLE

    if result.returncode != 0:
        return GIT_SHA_UNAVAILABLE

    sha = (result.stdout or "").strip()
    return sha or GIT_SHA_UNAVAILABLE


def dependency_versions(names: Sequence[str] = TRACKED_DEPENDENCIES) -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in names:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "not installed"
    return versions


@dataclass
class FileRecord:
    path: str
    sha256: str
    size_bytes: int
    row_count: int | None = None

    @classmethod
    def build(
        cls,
        path: Path,
        relative_to: Path | None = None,
        fallback_relative_to: Path | None = None,
    ) -> "FileRecord":
        display = path
        if relative_to is not None:
            try:
                display = path.relative_to(relative_to)
            except ValueError:
                if fallback_relative_to is not None:
                    try:
                        display = path.relative_to(fallback_relative_to)
                    except ValueError:
                        display = path

        return cls(
            path=display.as_posix(),
            sha256=hash_file(path),
            size_bytes=path.stat().st_size,
            row_count=count_csv_rows(path),
        )


@dataclass
class RunManifest:
    manifest_version: str
    run_id: str
    generated_at_utc: str
    client: str | None
    pilot: str | None
    execution_mode: str | None
    module: str | None
    git_commit_sha: str
    python_version: str
    platform: str
    dependency_versions: dict[str, str]
    inputs: list[FileRecord] = field(default_factory=list)
    inputs_combined_sha256: str = ""
    config_files: list[FileRecord] = field(default_factory=list)
    config_combined_sha256: str = ""
    outputs: list[FileRecord] = field(default_factory=list)
    outputs_combined_sha256: str = ""
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_manifest(
    client: str | None = None,
    pilot: str | None = None,
    execution_mode: str | None = None,
    module: str | None = None,
    input_paths: Iterable[Path] = (),
    config_paths: Iterable[Path] = (),
    relative_to: Path | None = None,
    repo_root: Path | None = None,
    run_id: str | None = None,
) -> RunManifest:
    """Build a manifest for a run. Missing input or config files are skipped."""
    inputs = [
        FileRecord.build(Path(p), relative_to, repo_root)
        for p in input_paths
        if Path(p).is_file()
    ]
    configs = [
        FileRecord.build(Path(p), relative_to, repo_root)
        for p in config_paths
        if Path(p).is_file()
    ]

    return RunManifest(
        manifest_version=MANIFEST_VERSION,
        run_id=run_id or uuid.uuid4().hex,
        generated_at_utc=datetime.now(timezone.utc).isoformat(),
        client=client,
        pilot=pilot,
        execution_mode=execution_mode,
        module=module,
        git_commit_sha=discover_git_sha(repo_root),
        python_version=platform.python_version(),
        platform=f"{platform.system()} {platform.release()}",
        dependency_versions=dependency_versions(),
        inputs=inputs,
        inputs_combined_sha256=combined_digest(r.sha256 for r in inputs),
        config_files=configs,
        config_combined_sha256=combined_digest(r.sha256 for r in configs),
        notes=[
            "Contains file digests and row counts only; no payroll records or "
            "personal information.",
            "Output hashing is populated only where a caller supplies output "
            "paths; see docs/operations/run_provenance.md.",
        ],
    )


def add_outputs(
    manifest: RunManifest,
    output_paths: Iterable[Path],
    relative_to: Path | None = None,
) -> RunManifest:
    """Record generated outputs on an existing manifest."""
    records = [
        FileRecord.build(Path(p), relative_to)
        for p in output_paths
        if Path(p).is_file()
    ]
    manifest.outputs = records
    manifest.outputs_combined_sha256 = combined_digest(r.sha256 for r in records)
    return manifest


def write_manifest(
    manifest: RunManifest,
    outputs_dir: Path,
    filename: str | None = None,
) -> Path:
    """Write the manifest as JSON into the pilot's outputs directory."""
    outputs_dir = Path(outputs_dir)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    path = outputs_dir / (filename or manifest_filename(manifest.module or "run"))
    payload = json.dumps(manifest.to_dict(), indent=2, sort_keys=False)
    path.write_text(payload + "\n", encoding="utf-8")
    return path


def read_manifest(outputs_dir: Path, filename: str) -> dict[str, Any]:
    path = Path(outputs_dir) / filename
    return json.loads(path.read_text(encoding="utf-8"))
