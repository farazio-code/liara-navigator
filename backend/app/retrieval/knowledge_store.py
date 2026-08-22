from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.domain.errors import AppError, ErrorCode

Topic = Literal["paas", "cdn", "ssl", "dns", "other"]
TOKEN_PATTERN = re.compile(r"[\w.-]+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class KnowledgeChunk:
    chunk_id: str
    title: str
    heading: str
    url: str
    topic: Topic
    platform: str | None
    content: str


@dataclass(frozen=True, slots=True)
class SearchHit:
    chunk_id: str
    title: str
    heading: str
    url: str
    topic: Topic
    platform: str | None
    preview: str
    score: float


@dataclass(slots=True)
class ReadBudget:
    max_chunks: int = 5
    max_chars: int = 6000
    used_chunks: int = 0
    used_chars: int = 0

    def can_read(self, content: str) -> bool:
        within_chunk_limit = self.used_chunks < self.max_chunks
        within_character_limit = self.used_chars + len(content) <= self.max_chars
        return within_chunk_limit and within_character_limit

    def consume(self, content: str) -> None:
        self.used_chunks += 1
        self.used_chars += len(content)


class KnowledgeStore:
    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self._chunks = {chunk.chunk_id: chunk for chunk in chunks}

    @classmethod
    def from_jsonl(cls, path: Path) -> KnowledgeStore:
        chunks: list[KnowledgeChunk] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                chunks.append(KnowledgeChunk(**json.loads(line)))
        return cls(chunks)

    def search(self, query: str, *, topic: Topic, limit: int = 10) -> list[SearchHit]:
        query_tokens = _tokens(query)
        ranked: list[tuple[float, KnowledgeChunk]] = []
        for chunk in self._chunks.values():
            if chunk.topic != topic:
                continue
            searchable = f"{chunk.title} {chunk.heading} {chunk.content} {chunk.platform or ''}"
            chunk_tokens = _tokens(searchable)
            overlap = len(query_tokens & chunk_tokens)
            phrase_bonus = 2 if _normalize(query) in _normalize(searchable) else 0
            score = float(overlap + phrase_bonus)
            if score > 0:
                ranked.append((score, chunk))
        ranked.sort(key=lambda item: (-item[0], item[1].chunk_id))
        return [
            SearchHit(
                chunk_id=chunk.chunk_id,
                title=chunk.title,
                heading=chunk.heading,
                url=chunk.url,
                topic=chunk.topic,
                platform=chunk.platform,
                preview=chunk.content[:177] + ("…" if len(chunk.content) > 177 else ""),
                score=score,
            )
            for score, chunk in ranked[: max(1, min(limit, 10))]
        ]

    def read_docs(self, chunk_ids: list[str], *, budget: ReadBudget) -> list[KnowledgeChunk]:
        selected: list[KnowledgeChunk] = []
        for chunk_id in chunk_ids:
            chunk = self._chunks.get(chunk_id)
            if chunk is None:
                raise AppError(ErrorCode.SOURCE_NOT_FOUND)
            if not budget.can_read(chunk.content):
                break
            budget.consume(chunk.content)
            selected.append(chunk)
        return selected


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("ي", "ی").replace("ك", "ک").split())


def _tokens(value: str) -> set[str]:
    normalized = _normalize(value)
    synonyms = {"گزارش": "لاگ", "گواهی": "ssl", "دامنه": "dns", "برنامه": "app"}
    return {synonyms.get(token, token) for token in TOKEN_PATTERN.findall(normalized)}
