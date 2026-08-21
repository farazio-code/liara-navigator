from __future__ import annotations

import json

import httpx
import pytest
from app.config import Settings
from app.main import create_app
from app.providers.ai.base import CompletionResult


class ContextCapturingProvider:
    def __init__(self) -> None:
        self.contexts: list[list[str]] = []

    async def complete(self, *, message: str, topic: str, context: list[str]) -> CompletionResult:
        self.contexts.append(context)
        return CompletionResult(
            claims=[
                {
                    "text": "ابتدا دسترسی شبکه داخلی دیتابیس را بررسی کنید.",
                    "role": "core",
                    "chunk_id": "paas-database-connection",
                    "evidence": "دسترسی شبکه داخلی را بررسی کنید",
                }
            ]
        )


def settings() -> Settings:
    return Settings(
        _env_file=None,
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://navigator:navigator@localhost:5432/navigator",
        SESSION_HMAC_SECRET="s" * 32,
        AVALAI_API_KEY="test-api-key-not-a-real-secret",
    )


@pytest.mark.asyncio
async def test_paas_turn_fetches_logs_once_without_returning_raw_content() -> None:
    provider = ContextCapturingProvider()
    app = create_app(settings(), ai_provider=provider)
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        session = await client.post("/api/v1/sessions")
        csrf = session.json()["csrf_token"]
        selected_app = (
            await client.get("/api/v1/fake-liara/apps", params={"platform": "django"})
        ).json()["apps"][0]
        service = (
            await client.get(f"/api/v1/fake-liara/apps/{selected_app['ref']}/services")
        ).json()["services"][0]
        response = await client.post(
            "/api/v1/turns/stream",
            headers={"X-CSRF-Token": csrf},
            json={
                "client_request_id": "turn-paas-0001",
                "topic": "paas",
                "message": "برنامه بالا می‌آید اما اتصال دیتابیس timeout می‌شود",
                "service_ref": service["ref"],
            },
        )

    assert response.status_code == 200
    assert response.text.count("event: agent.fetching_logs") == 1
    assert "Database connection timed out" not in response.text
    assert len(provider.contexts) == 1
    assert "<UNTRUSTED_SERVICE_LOGS>" in provider.contexts[0][-1]
    terminal = json.loads(
        next(
            line.removeprefix("data: ")
            for block in response.text.split("\n\n")
            if block.startswith("event: request.completed")
            for line in block.splitlines()
            if line.startswith("data: ")
        )
    )
    assert terminal["status"] == "answer"


@pytest.mark.asyncio
async def test_paas_turn_denies_a_service_reference_from_another_session() -> None:
    app = create_app(settings(), ai_provider=ContextCapturingProvider())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as owner,
        httpx.AsyncClient(transport=transport, base_url="http://test") as stranger,
    ):
        await owner.post("/api/v1/sessions")
        selected_app = (
            await owner.get("/api/v1/fake-liara/apps", params={"platform": "django"})
        ).json()["apps"][0]
        service = (
            await owner.get(f"/api/v1/fake-liara/apps/{selected_app['ref']}/services")
        ).json()["services"][0]
        stranger_session = await stranger.post("/api/v1/sessions")
        denied = await stranger.post(
            "/api/v1/turns/stream",
            headers={"X-CSRF-Token": stranger_session.json()["csrf_token"]},
            json={
                "client_request_id": "turn-paas-0002",
                "topic": "paas",
                "message": "این سرویس چرا با خطای timeout روبه‌رو می‌شود؟",
                "service_ref": service["ref"],
            },
        )

    assert denied.status_code == 404
    assert denied.json()["code"] == "RESOURCE_NOT_ALLOWED"
