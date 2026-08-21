from pathlib import Path

import pytest
from app.application.agent import BoundedAgent
from app.domain.errors import AppError, ErrorCode
from app.providers.ai.base import CompletionResult
from app.providers.ai.fixture import FixtureAIProvider
from app.retrieval.knowledge_store import KnowledgeStore

FIXTURE = Path(__file__).parents[3] / "knowledge" / "snapshots" / "test-fixture" / "chunks.jsonl"


class CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def complete(self, *, message: str, topic: str, context: list[str]) -> CompletionResult:
        self.calls += 1
        evidence = "رکورد DNS مناسب را در ناحیه دامنه ایجاد کنید"
        return CompletionResult(
            claims=[
                {
                    "text": "رکورد DNS مناسب را ایجاد و انتشار آن را بررسی کنید.",
                    "role": "core",
                    "chunk_id": "dns-records",
                    "evidence": evidence,
                }
            ]
        )


@pytest.mark.asyncio
async def test_general_agent_searches_reads_and_returns_validated_citations() -> None:
    provider = CountingProvider()
    agent = BoundedAgent(store=KnowledgeStore.from_jsonl(FIXTURE), provider=provider)

    result = await agent.run(topic="dns", message="دامنه من به برنامه متصل نمی‌شود")

    assert result.status == "answer"
    assert result.claims[0].citation.chunk_id == "dns-records"
    assert result.model_calls == 1
    assert result.read_chunks <= 3
    assert provider.calls == 1


@pytest.mark.asyncio
async def test_short_question_clarifies_without_spending_a_model_call() -> None:
    provider = CountingProvider()
    agent = BoundedAgent(store=KnowledgeStore.from_jsonl(FIXTURE), provider=provider)

    result = await agent.run(topic="dns", message="خطا دارم")

    assert result.status == "clarification"
    assert result.model_calls == 0
    assert provider.calls == 0


@pytest.mark.asyncio
async def test_no_evidence_returns_unknown_without_calling_the_model() -> None:
    provider = CountingProvider()
    agent = BoundedAgent(store=KnowledgeStore.from_jsonl(FIXTURE), provider=provider)

    result = await agent.run(topic="cdn", message="مشکل ناشناخته ZXQ-991 در سرویس من چیست؟")

    assert result.status == "unknown"
    assert result.model_calls == 0
    assert provider.calls == 0


@pytest.mark.parametrize(
    ("topic", "message"),
    [
        ("cdn", "بعد از تغییر فایل‌های استاتیک نسخه قدیمی نمایش داده می‌شود"),
        ("ssl", "برای دامنه من گواهی SSL صادر نمی‌شود و DNS تنظیم است"),
        ("dns", "رکورد دامنه هنوز برنامه را نشان نمی‌دهد"),
    ],
)
@pytest.mark.asyncio
async def test_supported_general_topics_finish_with_a_cited_answer(
    topic: str, message: str
) -> None:
    agent = BoundedAgent(store=KnowledgeStore.from_jsonl(FIXTURE), provider=FixtureAIProvider())

    result = await agent.run(topic=topic, message=message)  # type: ignore[arg-type]

    assert result.status == "answer"
    assert result.claims
    assert result.model_calls == 1


class FailingProvider:
    async def complete(self, *, message: str, topic: str, context: list[str]) -> CompletionResult:
        raise AppError(ErrorCode.AI_TIMEOUT)


@pytest.mark.asyncio
async def test_provider_failure_is_bounded_and_propagates_as_a_safe_error() -> None:
    agent = BoundedAgent(store=KnowledgeStore.from_jsonl(FIXTURE), provider=FailingProvider())

    with pytest.raises(AppError) as caught:
        await agent.run(topic="dns", message="دامنه من به برنامه متصل نمی‌شود")

    assert caught.value.code == ErrorCode.AI_TIMEOUT
