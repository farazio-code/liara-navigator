from __future__ import annotations

from pathlib import Path

import pytest
from app.domain.errors import AppError, ErrorCode
from app.retrieval.knowledge_store import KnowledgeStore, ReadBudget

FIXTURE = Path(__file__).parents[3] / "knowledge" / "snapshots" / "test-fixture" / "chunks.jsonl"


def test_search_returns_small_metadata_results_before_full_chunks() -> None:
    store = KnowledgeStore.from_jsonl(FIXTURE)

    results = store.search("خطای اتصال دیتابیس در django", topic="paas", limit=3)

    assert results
    assert results[0].topic == "paas"
    assert results[0].preview
    assert len(results[0].preview) <= 180
    assert not hasattr(results[0], "content")


def test_read_doc_is_manifest_bound_and_consumes_a_per_turn_budget() -> None:
    store = KnowledgeStore.from_jsonl(FIXTURE)
    result_ids = [item.chunk_id for item in store.search("لاگ برنامه", topic="paas")]
    budget = ReadBudget(max_chunks=2, max_chars=500)

    chunks = store.read_docs(result_ids, budget=budget)

    assert 1 <= len(chunks) <= 2
    assert sum(len(item.content) for item in chunks) <= 500
    assert budget.used_chunks == len(chunks)
    assert budget.used_chars == sum(len(item.content) for item in chunks)

    with pytest.raises(AppError) as caught:
        store.read_docs(["../../etc/passwd"], budget=budget)
    assert caught.value.code == ErrorCode.SOURCE_NOT_FOUND


def test_topic_filter_prevents_unrelated_document_expansion() -> None:
    store = KnowledgeStore.from_jsonl(FIXTURE)

    results = store.search("تنظیم دامنه", topic="dns", limit=5)

    assert results
    assert {item.topic for item in results} == {"dns"}
