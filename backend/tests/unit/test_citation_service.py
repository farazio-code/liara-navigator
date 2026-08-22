from app.application.citation_service import CitationService, DraftClaim
from app.retrieval.knowledge_store import KnowledgeChunk


def chunk(chunk_id: str, content: str) -> KnowledgeChunk:
    return KnowledgeChunk(
        chunk_id=chunk_id,
        title="راهنمای تست",
        heading="بخش تست",
        url="https://docs.liara.ir/test",
        topic="paas",
        platform=None,
        content=content,
    )


def test_invalid_core_claim_turns_the_whole_answer_into_unknown() -> None:
    service = CitationService()
    result = service.validate(
        [DraftClaim(text="پورت باید ۸۰ باشد", role="core", chunk_id="c1", evidence="پورت ۸۰")],
        {"c1": chunk("c1", "برنامه باید روی پورت ۸۰۸۰ گوش دهد.")},
    )

    assert result.status == "unknown"
    assert result.claims == []


def test_invalid_supporting_claim_is_dropped_but_core_answer_remains() -> None:
    service = CitationService()
    result = service.validate(
        [
            DraftClaim(
                text="برنامه باید روی پورت ۸۰۸۰ گوش دهد.",
                role="core",
                chunk_id="c1",
                evidence="پورت ۸۰۸۰",
            ),
            DraftClaim(
                text="همیشه از نسخه آزمایشی استفاده کنید",
                role="supporting",
                chunk_id="c1",
                evidence="نسخه آزمایشی",
            ),
        ],
        {"c1": chunk("c1", "برنامه باید روی پورت ۸۰۸۰ گوش دهد.")},
    )

    assert result.status == "answer"
    assert len(result.claims) == 1
    assert result.claims[0].citation.url == "https://docs.liara.ir/test"
