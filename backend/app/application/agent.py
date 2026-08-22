from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Any, Dict

from app.application.citation_service import (
    CitationService,
    DraftClaim,
    ValidatedClaim,
)
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
    def __init__(
        self,
        *,
        store: KnowledgeStore,
        provider: AIProvider,
    ) -> None:
        self._store = store
        self._provider = provider
        self._citations = CitationService()

    @staticmethod
    def _clean_and_normalize_claim(
        claim: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        پاکسازی و نرمال‌سازی claim خروجی مدل برای تطابق با DraftClaim.

        هدف:
        - حذف فیلدهای اضافی مثل exact_evidence
        - تبدیل citation/source به evidence در صورت نیاز
        - عدم ساخت evidence جعلی
        """

        cleaned = dict(claim)

        # ---------------------------------------------------------
        # 1. حذف فیلدهای اضافی که DraftClaim انتظار ندارد
        # ---------------------------------------------------------
        cleaned.pop("exact evidence", None)
        cleaned.pop("exact_evidence", None)

        # ---------------------------------------------------------
        # 2. نرمال‌سازی evidence
        # ---------------------------------------------------------
        if "evidence" not in cleaned:
            if "citation" in cleaned:
                cleaned["evidence"] = cleaned["citation"]

            elif "source" in cleaned:
                cleaned["evidence"] = cleaned["source"]

        return cleaned

    @staticmethod
    def _has_valid_evidence(claim: Dict[str, Any]) -> bool:
        """
        بررسی می‌کند claim واقعاً evidence دارد یا خیر.

        evidence خالی یا None معتبر نیست.
        """

        if "evidence" not in claim:
            return False

        evidence = claim.get("evidence")

        if evidence is None:
            return False

        if isinstance(evidence, str) and not evidence.strip():
            return False

        if isinstance(evidence, (list, tuple, set)) and not evidence:
            return False

        return True

    async def run(
        self,
        *,
        topic: Topic,
        message: str,
        runtime_evidence: str | None = None,
    ) -> AgentResult:

        # =========================================================
        # 1. Route topic
        # =========================================================

        decision = route_topic(topic)

        # =========================================================
        # 2. Validate user message
        # =========================================================

        if len(message.strip()) < 12:
            return AgentResult(
                status="clarification",
                claims=[],
                message=(
                    "لطفاً خطا، رفتار مشاهده‌شده و نتیجه مورد انتظار "
                    "را کمی دقیق‌تر بنویسید."
                ),
                model_calls=0,
                read_chunks=0,
            )

        # =========================================================
        # 3. Build search query
        # =========================================================

        search_query = message

        if runtime_evidence:
            search_query = (
                f"{message}\n"
                f"{runtime_evidence[:2000]}"
            )

        # =========================================================
        # 4. Search knowledge store
        # =========================================================

        hits = self._store.search(
            search_query,
            topic=decision.knowledge_topic,
            limit=5,
        )

        if not hits:
            return AgentResult(
                status="unknown",
                claims=[],
                message="پاسخ قابل اتکایی در منابع رسمی Liara پیدا نشد.",
                model_calls=0,
                read_chunks=0,
            )

        # =========================================================
        # 5. Read bounded context
        # =========================================================

        budget = ReadBudget(
            max_chunks=3,
            max_chars=3600,
        )

        chunks = self._store.read_docs(
            [hit.chunk_id for hit in hits],
            budget=budget,
        )

        # =========================================================
        # 6. Build model context
        # =========================================================

        context = [
            f"{chunk.chunk_id}\n{chunk.content}"
            for chunk in chunks
        ]

        if runtime_evidence:
            context.append(runtime_evidence)

        # =========================================================
        # 7. Call AI provider
        # =========================================================

        completion = await self._provider.complete(
            message=message,
            topic=topic,
            context=context,
        )

        # =========================================================
        # 8. Normalize claims
        # =========================================================

        cleaned_claims: list[Dict[str, Any]] = []

        for index, claim in enumerate(completion.claims):

            try:
                cleaned = self._clean_and_normalize_claim(claim)

            except Exception as exc:
                print(
                    f"[AGENT] Failed to normalize claim #{index}: "
                    f"{exc!r}"
                )
                print(
                    f"[AGENT] Original claim: {claim!r}"
                )
                continue

            print(
                f"[AGENT] Claim #{index} keys: "
                f"{list(cleaned.keys())}"
            )

            # -----------------------------------------------------
            # Claim بدون evidence را وارد DraftClaim نکن
            # -----------------------------------------------------

            if not self._has_valid_evidence(cleaned):
                print(
                    f"[AGENT] Skipping claim #{index}: "
                    f"missing evidence"
                )
                print(
                    f"[AGENT] Claim content: {cleaned!r}"
                )
                continue

            cleaned_claims.append(cleaned)

        # =========================================================
        # 9. No valid claims
        # =========================================================

        if not cleaned_claims:
            print(
                "[AGENT] No claims with valid evidence were produced."
            )

            return AgentResult(
                status="unknown",
                claims=[],
                message=(
                    "پاسخ تولیدشده فاقد evidence معتبر برای استناد "
                    "به منابع رسمی بود."
                ),
                model_calls=1,
                read_chunks=len(chunks),
            )

        # =========================================================
        # 10. Build DraftClaim objects
        # =========================================================

        drafts: list[DraftClaim] = []

        for index, claim in enumerate(cleaned_claims):

            try:
                draft = DraftClaim(**claim)
                drafts.append(draft)

            except TypeError as exc:
                print(
                    f"[AGENT] Failed to create DraftClaim "
                    f"for claim #{index}: {exc!r}"
                )

                print(
                    f"[AGENT] Claim keys: {list(claim.keys())}"
                )

                print(
                    f"[AGENT] Claim value: {claim!r}"
                )

                continue

        # =========================================================
        # 11. No DraftClaim objects
        # =========================================================

        if not drafts:
            return AgentResult(
                status="unknown",
                claims=[],
                message=(
                    "ساختار پاسخ تولیدشده با قالب مورد انتظار "
                    "سیستم استناد سازگار نبود."
                ),
                model_calls=1,
                read_chunks=len(chunks),
            )

        # =========================================================
        # 12. Citation validation
        # =========================================================

        cited = self._citations.validate(
            drafts,
            {
                chunk.chunk_id: chunk
                for chunk in chunks
            },
        )

        # =========================================================
        # 13. Citation validation failed
        # =========================================================

        if cited.status == "unknown":
            return AgentResult(
                status="unknown",
                claims=[],
                message=(
                    "پاسخ تولیدشده پشتوانه کافی در منابع رسمی نداشت."
                ),
                model_calls=1,
                read_chunks=len(chunks),
            )

        # =========================================================
        # 14. Successful answer
        # =========================================================

        return AgentResult(
            status="answer",
            claims=cited.claims,
            message="",
            model_calls=1,
            read_chunks=len(chunks),
        )
