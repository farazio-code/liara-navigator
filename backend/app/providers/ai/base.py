from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Protocol, TypedDict


class ClaimPayload(TypedDict):
    text: str
    role: Literal["core", "supporting"]
    chunk_id: str
    evidence: str


@dataclass(frozen=True, slots=True)
class CompletionResult:
    claims: list[ClaimPayload]


class AIProvider(Protocol):
    async def complete(
        self, *, message: str, topic: str, context: list[str]
    ) -> CompletionResult: ...
