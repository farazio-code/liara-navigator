from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Any, Dict

from app.application.citation_service import CitationService, DraftClaim, ValidatedClaim
from app.application.router import Topic, route_topic
from app.providers.ai.base import AIProvider
from app.retrieval.knowledge_store import KnowledgeStore, ReadBudget


@dataclass(frozen=True, slots=True)
class AgentResult:
    status: Literal["answer", "unknown", "clarification"]
    claims: list[ValidatedClaim]
    message: str
    model_calls: int
    read_chunks: int


class BoundedAgent:
    def __init__(self, *, store: KnowledgeStore, provider: AIProvider) -> None:
        self._store = store
        self._provider = provider
        self._citations = CitationService()

    @staticmethod
    def _clean_claim(claim: Dict[str, Any]) -> Dict[str, Any]:
        """پاکسازی کلیدهای ناخواسته از دیکشنری claim"""
        cleaned = claim.copy()
        # حذف کلیدهای مشکل‌دار (هر دو حالت)
        cleaned.pop('exact evidence', None)  # با فاصله
        cleaned.pop('exact_evidence', None)  # با آندرلاین
        # در صورت نیاز، کلیدهای دیگری که باعث خطا می‌شوند را اینجا اضافه کنید
        return cleaned

    async def run(
        self, *, topic: Topic, message: str, runtime_evidence: str | None = None
    ) -> AgentResult:
        decision = route_topic(topic)
        if len(message.strip()) < 12:
            return AgentResult(
                status="clarification",
                claims=[],
                message="لطفاً خطا، رفتار مشاهده‌شده و نتیجه مورد انتظار را کمی دقیق‌تر بنویسید.",
                model_calls=0,
                read_chunks=0,
            )
        search_query = message
        if runtime_evidence:
            search_query = f"{message}\n{runtime_evidence[:2000]}"
        hits = self._store.search(search_query, topic=decision.knowledge_topic, limit=5)
        if not hits:
            return AgentResult(
                status="unknown",
                claims=[],
                message="پاسخ قابل اتکایی در منابع رسمی Liara پیدا نشد.",
                model_calls=0,
                read_chunks=0,
            )
        budget = ReadBudget(max_chunks=3, max_chars=3600)
        chunks = self._store.read_docs([hit.chunk_id for hit in hits], budget=budget)
        context = [f"{chunk.chunk_id}\n{chunk.content}" for chunk in chunks]
        if runtime_evidence:
            context.append(runtime_evidence)
        completion = await self._provider.complete(
            message=message,
            topic=topic,
            context=context,
        )
        
        # پاکسازی claims قبل از ساخت DraftClaim
        cleaned_claims = [self._clean_claim(claim) for claim in completion.claims]
        drafts = [DraftClaim(**claim) for claim in cleaned_claims]
        
        cited = self._citations.validate(drafts, {chunk.chunk_id: chunk for chunk in chunks})
        if cited.status == "unknown":
            return AgentResult(
                status="unknown",
                claims=[],
                message="پاسخ تولیدشده پشتوانه کافی در منابع رسمی نداشت.",
                model_calls=1,
                read_chunks=len(chunks),
            )
        return AgentResult(
            status="answer",
            claims=cited.claims,
            message="",
            model_calls=1,
            read_chunks=len(chunks),
        )
