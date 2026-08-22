#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "backend"))

from app.retrieval.snapshot_builder import SOURCE_REPOSITORY, build_snapshot  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build an immutable Liara documentation snapshot for Liara Navigator."
    )
    parser.add_argument("--repo-path", type=Path, help="Existing liara-cloud/docs checkout")
    parser.add_argument(
        "--output-root",
        type=Path,
        default=PROJECT_ROOT / "knowledge" / "snapshots",
    )
    parser.add_argument("--docs-subdir", default="src/pages")
    parser.add_argument("--base-url", default="https://docs.liara.ir")
    parser.add_argument("--max-chars", type=int, default=1600)
    parser.add_argument("--min-chunks", type=int, default=100)
    args = parser.parse_args()

    temporary = (
        tempfile.TemporaryDirectory(prefix="liara-docs-")
        if args.repo_path is None
        else nullcontext()
    )
    with temporary as temporary_directory:
        if args.repo_path is None:
            repo_path = Path(str(temporary_directory)) / "docs"
            subprocess.run(
                ["git", "clone", "--depth", "1", SOURCE_REPOSITORY, str(repo_path)],
                check=True,
            )
        else:
            repo_path = args.repo_path.resolve()
        result = build_snapshot(
            repo_path,
            args.output_root.resolve(),
            docs_subdir=args.docs_subdir,
            base_url=args.base_url,
            max_chars=args.max_chars,
            min_chunks=args.min_chunks,
        )

    print(
        json.dumps(
            {
                "snapshot_version": result.version,
                "source_commit": result.source_commit,
                "chunk_count": result.chunk_count,
                "topic_counts": result.topic_counts,
                "output_directory": str(result.directory),
                "liara_environment": {
                    "KNOWLEDGE_SNAPSHOT_VERSION": result.version,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
