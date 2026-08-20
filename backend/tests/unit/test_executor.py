from __future__ import annotations

import asyncio
import threading
import time

import httpx
import pytest

from app.api.dependencies import BoundedExecutor
from app.config import Settings
from app.main import create_app


def make_settings() -> Settings:
    return Settings(
        _env_file=None,
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://navigator:navigator@localhost:5432/navigator",
        SESSION_HMAC_SECRET="s" * 32,
        AVALAI_API_KEY="test-api-key-not-a-real-secret",
        CPU_EXECUTOR_WORKERS=2,
    )


@pytest.mark.asyncio
async def test_bounded_executor_keeps_health_request_non_blocking() -> None:
    executor = BoundedExecutor(max_workers=2)
    app = create_app(make_settings(), executor=executor)
    transport = httpx.ASGITransport(app=app)
    worker_finished = threading.Event()

    def blocking_operation() -> None:
        time.sleep(0.25)
        worker_finished.set()

    async with app.router.lifespan_context(app):
        blocking_work = asyncio.create_task(executor.run(blocking_operation))
        await asyncio.sleep(0.02)
        started = time.perf_counter()
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/v1/health/live")
        elapsed = time.perf_counter() - started
        await asyncio.sleep(0.3)
        blocking_work.cancel()
        await asyncio.gather(blocking_work, return_exceptions=True)

    assert executor.max_workers == 2
    assert worker_finished.is_set()
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}
    assert elapsed < 0.15
