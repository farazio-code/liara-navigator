from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.domain.errors import AppError, ErrorCode
from app.retrieval.source_policy import is_allowed_source


@dataclass(frozen=True, slots=True)
class SnapshotManifest:
    schema_version: int
    version: str
    chunk_count: int
    chunks_sha256: str


def validate_snapshot(directory: Path) -> SnapshotManifest:
    try:
        manifest = SnapshotManifest(**json.loads((directory / "manifest.json").read_text()))
        chunks_bytes = (directory / "chunks.jsonl").read_bytes()
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise AppError(ErrorCode.SNAPSHOT_INCOMPATIBLE) from error
    if manifest.schema_version != 1:
        raise AppError(ErrorCode.SNAPSHOT_INCOMPATIBLE)
    if hashlib.sha256(chunks_bytes).hexdigest() != manifest.chunks_sha256:
        raise AppError(ErrorCode.SNAPSHOT_INCOMPATIBLE)
    rows = [json.loads(line) for line in chunks_bytes.decode().splitlines() if line.strip()]
    if len(rows) != manifest.chunk_count or not all(is_allowed_source(row["url"]) for row in rows):
        raise AppError(ErrorCode.SNAPSHOT_INCOMPATIBLE)
    return manifest
