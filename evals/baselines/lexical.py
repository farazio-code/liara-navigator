from __future__ import annotations

import json
from pathlib import Path

from app.retrieval.knowledge_store import KnowledgeStore


ROOT = Path(__file__).parents[2]


def run() -> dict[str, float | int]:
    store = KnowledgeStore.from_jsonl(
        ROOT / "knowledge" / "snapshots" / "test-fixture" / "chunks.jsonl"
    )
    cases = [
        json.loads(line)
        for line in (ROOT / "evals" / "golden-set" / "cases.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    correct = 0
    for case in cases:
        hits = store.search(case["question"], topic=case["topic"], limit=1)
        actual = hits[0].chunk_id if hits else None
        correct += int(actual == case["expected_chunk"])
    return {"cases": len(cases), "top_1_accuracy": correct / len(cases)}


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
