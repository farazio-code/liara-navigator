from __future__ import annotations

import json

import httpx
import pytest
from app.config import Settings
from app.main import create_app
from app.providers.ai.base import CompletionResult


class StubProvider:
    async def complete(self, *, message: str, topic: str, context: list[str]) -> CompletionResult:
        return CompletionResult(
            claims=[
                {
                    "text": "رکورد DNS را بررسی کنید.",
                    "role": "core",
                    "chunk_id": "dns-records",
                    "evidence": "رکورد DNS مناسب را در ناحیه دامنه ایجاد کنید",
                }
            ]
        )


def make_settings() -> Settings:
    return Settings(
        _env_file=None,
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://navigator:navigator@localhost:5432/navigator",
        SESSION_HMAC_SECRET="s" * 32,
        AVALAI_API_KEY="test-api-key-not-a-real-secret",
    )


def parse_sse(body: str) -> list[tuple[str, dict[str, object]]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = block.splitlines()
        name = lines[0].removeprefix("event: ")
        payload = json.loads(lines[1].removeprefix("data: "))
        events.append((name, payload))
    return events


@pytest.mark.asyncio
async def test_turn_stream_is_typed_terminal_and_idempotent() -> None:
    app = create_app(make_settings(), ai_provider=StubProvider())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        session = await client.post("/api/v1/sessions")
        csrf = session.json()["csrf_token"]
        request = {
            "client_request_id": "turn-dns-0001",
            "topic": "dns",
            "message": "دامنه من به برنامه متصل نمی‌شود",
        }
        first = await client.post(
            "/api/v1/turns/stream", json=request, headers={"X-CSRF-Token": csrf}
        )
        repeated = await client.post(
            "/api/v1/turns/stream", json=request, headers={"X-CSRF-Token": csrf}
        )

    assert first.status_code == 200
    assert first.headers["content-type"].startswith("text/event-stream")
    assert repeated.text == first.text
    events = parse_sse(first.text)
    assert [name for name, _ in events] == [
        "request.accepted",
        "agent.searching",
        "agent.reading",
        "request.completed",
    ]
    assert events[-1][1]["status"] == "answer"


@pytest.mark.asyncio
async def test_turn_rejects_bad_csrf_and_idempotency_conflict() -> None:
    app = create_app(make_settings(), ai_provider=StubProvider())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        session = await client.post("/api/v1/sessions")
        csrf = session.json()["csrf_token"]
        request = {
            "client_request_id": "turn-dns-0002",
            "topic": "dns",
            "message": "دامنه من به برنامه متصل نمی‌شود",
        }
        denied = await client.post(
            "/api/v1/turns/stream", json=request, headers={"X-CSRF-Token": "wrong"}
        )
        await client.post("/api/v1/turns/stream", json=request, headers={"X-CSRF-Token": csrf})
        request["message"] = "متن متفاوت برای همان شناسه درخواست"
        conflict = await client.post(
            "/api/v1/turns/stream", json=request, headers={"X-CSRF-Token": csrf}
        )

    assert denied.status_code == 403
    assert conflict.status_code == 409
