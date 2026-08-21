from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from app.retrieval.knowledge_store import KnowledgeChunk


@dataclass(frozen=True, slots=True)
class DraftClaim:
    text: str
    role: Literal["core", "supporting"]
    chunk_id: str
    evidence: str


@dataclass(frozen=True, slots=True)
class Citation:
    chunk_id: str
    title: str
    heading: str
    url: str
    evidence: str


@dataclass(frozen=True, slots=True)
class ValidatedClaim:
    text: str
    role: Literal["core", "supporting"]
    citation: Citation


@dataclass(frozen=True, slots=True)
class CitationResult:
    status: Literal["answer", "unknown"]
    claims: list[ValidatedClaim]


class CitationService:
    def validate(
        self, drafts: list[DraftClaim], chunks: dict[str, KnowledgeChunk]
    ) -> CitationResult:
        validated: list[ValidatedClaim] = []
        for draft in drafts:
            source = chunks.get(draft.chunk_id)
            evidence = draft.evidence.strip()
            if source is None or not re.search(
                rf"(?<!\w){re.escape(evidence)}(?!\w)", source.content
            ):
                if draft.role == "core":
                    return CitationResult(status="unknown", claims=[])
                continue
            validated.append(
                ValidatedClaim(
                    text=draft.text,
                    role=draft.role,
                    citation=Citation(
                        chunk_id=source.chunk_id,
                        title=source.title,
                        heading=source.heading,
                        url=source.url,
                        evidence=evidence,
                    ),
                )
            )
        if not any(claim.role == "core" for claim in validated):
            return CitationResult(status="unknown", claims=[])
        return CitationResult(status="answer", claims=validated)
