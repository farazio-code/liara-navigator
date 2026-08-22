from __future__ import annotations

import httpx
import pytest
from app.config import Settings
from app.main import create_app


def settings() -> Settings:
    return Settings(
        _env_file=None,
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://navigator:navigator@localhost:5432/navigator",
        SESSION_HMAC_SECRET="s" * 32,
        AVALAI_API_KEY="test-api-key-not-a-real-secret",
    )


@pytest.mark.asyncio
async def test_ticket_submission_is_strict_mocked_and_secret_safe() -> None:
    app = create_app(settings())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        session = await client.post("/api/v1/sessions")
        csrf = session.json()["csrf_token"]
        accepted = await client.post(
            "/api/v1/tickets",
            headers={"X-CSRF-Token": csrf},
            json={
                "topic": "dns",
                "subject": "دامنه به برنامه متصل نمی‌شود",
                "description": "رکورد دامنه تنظیم شده اما پاسخ مورد انتظار دریافت نمی‌شود.",
            },
        )
        rejected_secret = await client.post(
            "/api/v1/tickets",
            headers={"X-CSRF-Token": csrf},
            json={
                "topic": "paas",
                "subject": "خطای اتصال برنامه به دیتابیس",
                "description": "password=hunter2 در تنظیمات اتصال قرار دارد.",
            },
        )
        rejected_extra = await client.post(
            "/api/v1/tickets",
            headers={"X-CSRF-Token": csrf},
            json={
                "topic": "dns",
                "subject": "دامنه به برنامه متصل نمی‌شود",
                "description": "شرح کافی برای تیکت آزمایشی و بررسی تیم پشتیبانی.",
                "attachment": "raw.log",
            },
        )

    assert accepted.status_code == 201
    assert accepted.json()["ticket_ref"].startswith("tkt_")
    assert accepted.json()["status"] == "accepted_mock"
    assert rejected_secret.status_code == 422
    assert rejected_extra.status_code == 422
