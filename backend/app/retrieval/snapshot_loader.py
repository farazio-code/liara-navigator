from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from app.domain.errors import AppError, ErrorCode
from app.retrieval.source_policy import is_allowed_source

CHUNK_FIELDS = {"chunk_id", "title", "heading", "url", "topic", "platform", "content"}
TOPICS = {"paas", "cdn", "ssl", "dns", "other"}


@dataclass(frozen=True, slots=True)
class SnapshotManifest:
    schema_version: int
    version: str
    chunk_count: int
    chunks_sha256: str
    source_repository: str | None = None
    source_commit: str | None = None
    created_at: str | None = None
    topic_counts: dict[str, int] | None = None


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
    try:
        rows = [json.loads(line) for line in chunks_bytes.decode().splitlines() if line.strip()]
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AppError(ErrorCode.SNAPSHOT_INCOMPATIBLE) from error
    if len(rows) != manifest.chunk_count or not all(_valid_chunk(row) for row in rows):
        raise AppError(ErrorCode.SNAPSHOT_INCOMPATIBLE)
    return manifest


def _valid_chunk(row: object) -> bool:
    if not isinstance(row, dict) or set(row) != CHUNK_FIELDS:
        return False
    string_fields = ("chunk_id", "title", "heading", "url", "content")
    if any(not isinstance(row[field], str) or not row[field].strip() for field in string_fields):
        return False
    if row["topic"] not in TOPICS:
        return False
    if row["platform"] is not None and not isinstance(row["platform"], str):
        return False
    return is_allowed_source(row["url"])
