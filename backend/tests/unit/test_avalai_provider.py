from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any, cast

import pytest
from app.providers.ai.avalai import AvalAIProvider
from openai import AsyncOpenAI


class FakeCompletions:
    def __init__(self, content: str) -> None:
        self.content = content
        self.request: dict[str, Any] | None = None

    async def create(self, **request: Any) -> SimpleNamespace:
        self.request = request
        message = SimpleNamespace(content=self.content)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


class FakeClient:
    def __init__(self, content: str) -> None:
        self.completions = FakeCompletions(content)
        self.chat = SimpleNamespace(completions=self.completions)


@pytest.mark.asyncio
async def test_avalai_provider_builds_openai_compatible_request_and_parses_claims() -> None:
    claim = {
        "text": "Check the DNS record.",
        "role": "core",
        "chunk_id": "dns-records",
        "evidence": "create the required DNS record",
    }
    fake_client = FakeClient(json.dumps({"claims": [claim]}))
    provider = AvalAIProvider(
        api_key="test-api-key-not-a-real-secret",
        base_url="https://api.avalai.ir/v1",
        model="gpt-5.4-mini",
        client=cast(AsyncOpenAI, fake_client),
    )

    result = await provider.complete(
        message="My domain does not resolve.",
        topic="dns",
        context=["dns-records\ncreate the required DNS record"],
    )

    assert result.claims == [claim]
    assert fake_client.completions.request is not None
    assert fake_client.completions.request["model"] == "gpt-5.4-mini"
    assert fake_client.completions.request["response_format"] == {"type": "json_object"}
