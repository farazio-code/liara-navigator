from __future__ import annotations

import logging

import httpx
import pytest
from app.config import Settings
from app.main import create_app


def make_settings() -> Settings:
    return Settings(
        _env_file=None,
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://navigator:navigator@localhost:5432/navigator",
        SESSION_HMAC_SECRET="s" * 32,
        AVALAI_API_KEY="test-api-key-not-a-real-secret",
    )


@pytest.mark.asyncio
async def test_anonymous_session_uses_secure_cookie_csrf_and_no_store() -> None:
    app = create_app(make_settings())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        response = await client.post("/api/v1/sessions")

    assert response.status_code == 201
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["referrer-policy"] == "no-referrer"
    cookie = response.headers["set-cookie"].lower()
    assert "ln_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie
    csrf_token = response.json()["csrf_token"]
    assert len(csrf_token) >= 32
    assert csrf_token not in cookie


@pytest.mark.asyncio
async def test_request_logger_never_records_authorization(
    caplog: pytest.LogCaptureFixture,
) -> None:
    secret = "Bearer secret-value-that-must-not-be-logged"
    app = create_app(make_settings())
    transport = httpx.ASGITransport(app=app)
    with caplog.at_level(logging.INFO, logger="liara_navigator.http"):
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
                response = await client.get(
                    "/api/v1/health/live",
                    headers={"Authorization": secret, "X-Request-ID": "not-a-valid-uuid"},
                )

    assert response.status_code == 200
    rendered_logs = "\n".join(record.getMessage() for record in caplog.records)
    assert "secret-value-that-must-not-be-logged" not in rendered_logs
    assert "Authorization" not in rendered_logs
    assert response.headers["cache-control"] == "no-store"
