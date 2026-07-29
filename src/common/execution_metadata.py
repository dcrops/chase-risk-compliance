from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

from common.run_manifest import (
    add_outputs,
    build_manifest,
    manifest_filename,
    write_manifest,
)


def write_execution_metadata(
    output_dir: Path,
    module_name: str,
    mode: str,
    include_supporting: bool,
    run_manifest: str,
    git_commit_sha: str,
) -> Path:
    """Record per-module execution metadata.

    The columns present before the run manifest existed are retained so
    downstream readers keep working; run identity is extended with the code
    provenance needed to tie a module run back to a manifest.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        [
            {
                "module": module_name,
                "mode": mode,
                "include_supporting": include_supporting,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "git_commit_sha": git_commit_sha,
                "run_manifest": run_manifest,
            }
        ]
    )

    path = output_dir / f"{module_name.lower()}_execution_metadata.csv"
    df.to_csv(path, index=False)
    return path


def finalize_module_run(
    output_dir: Path,
    module_name: str,
    mode: str,
    include_supporting: bool,
    client: str | None = None,
    pilot: str | None = None,
    input_paths: list[Path] | None = None,
    config_paths: list[Path] | None = None,
    output_paths: list[Path] | None = None,
    pilot_root: Path | None = None,
    repo_root: Path | None = None,
) -> tuple[Path, Path]:
    """Write matching execution metadata and manifest for a completed module.

    The manifest is built first so metadata records the same Git SHA and the
    exact module-specific filename. Metadata is then included among the
    manifest's generated outputs before the manifest is written.
    """
    output_dir = Path(output_dir)
    pilot_root = Path(pilot_root) if pilot_root is not None else output_dir.parent
    filename = manifest_filename(module_name)

    manifest = build_manifest(
        client=client,
        pilot=pilot,
        execution_mode=mode,
        module=module_name,
        input_paths=input_paths or [],
        config_paths=config_paths or [],
        relative_to=pilot_root,
        repo_root=repo_root,
    )
    metadata_path = write_execution_metadata(
        output_dir=output_dir,
        module_name=module_name,
        mode=mode,
        include_supporting=include_supporting,
        run_manifest=filename,
        git_commit_sha=manifest.git_commit_sha,
    )
    add_outputs(
        manifest,
        [*(output_paths or []), metadata_path],
        relative_to=pilot_root,
    )
    manifest_path = write_manifest(manifest, output_dir, filename=filename)
    return metadata_path, manifest_path
