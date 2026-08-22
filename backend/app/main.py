from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.dependencies import BoundedExecutor
from app.api.errors import ErrorJSONResponse, error_response
from app.api.middleware import SecurityMiddleware
from app.api.routes import fake_liara, health, sessions, tickets, turns
from app.application.agent import BoundedAgent
from app.config import Settings
from app.domain.errors import AppError
from app.providers.ai.avalai import AvalAIProvider
from app.providers.ai.base import AIProvider
from app.providers.ai.fixture import FixtureAIProvider
from app.providers.fake_liara.client import FakeLiaraClient
from app.retrieval.knowledge_store import KnowledgeStore
from app.retrieval.snapshot_loader import validate_snapshot
from app.security.rate_limit import MemoryRateLimiter
from app.security.session_vault import MemorySessionVault
from app.telemetry.store import MemoryTelemetryStore


def create_app(
    settings: Settings | None = None,
    *,
    executor: BoundedExecutor | None = None,
    ai_provider: AIProvider | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        resolved_settings = settings or Settings()
        resolved_executor = executor or BoundedExecutor(
            max_workers=resolved_settings.CPU_EXECUTOR_WORKERS
        )
        application.state.settings = resolved_settings
        application.state.executor = resolved_executor
        application.state.session_vault = MemorySessionVault(
            hmac_secret=resolved_settings.SESSION_HMAC_SECRET.get_secret_value()
        )
        application.state.fake_liara = FakeLiaraClient()
        application.state.telemetry = MemoryTelemetryStore()
        application.state.rate_limiter = MemoryRateLimiter()
        snapshot_directory = (
            Path(__file__).resolve().parents[2]
            / "knowledge"
            / "snapshots"
            / resolved_settings.KNOWLEDGE_SNAPSHOT_VERSION
        )
        validate_snapshot(snapshot_directory)
        snapshot_path = snapshot_directory / "chunks.jsonl"
        provider = ai_provider
        if provider is None:
            provider = (
                FixtureAIProvider()
                if resolved_settings.APP_ENV == "test"
                else AvalAIProvider(
                    api_key=resolved_settings.AVALAI_API_KEY.get_secret_value(),
                    base_url=str(resolved_settings.AI_BASE_URL),
                    model=resolved_settings.AI_FAST_MODEL,
                )
            )
        application.state.agent = BoundedAgent(
            store=KnowledgeStore.from_jsonl(snapshot_path), provider=provider
        )
        try:
            yield
        finally:
            application.state.session_vault.clear()
            await resolved_executor.aclose()

    application = FastAPI(
        title="Liara Navigator Internal API",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.add_middleware(SecurityMiddleware)
    application.include_router(sessions.router, prefix="/api/v1")
    application.include_router(fake_liara.router, prefix="/api/v1")
    application.include_router(turns.router, prefix="/api/v1")
    application.include_router(tickets.router, prefix="/api/v1")
    application.include_router(health.router, prefix="/api/v1")

    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    if frontend_dist.joinpath("index.html").exists():
        assets = frontend_dist / "assets"
        if assets.exists():
            application.mount("/assets", StaticFiles(directory=assets), name="assets")

        @application.get("/{full_path:path}", include_in_schema=False)
        async def frontend_fallback(full_path: str) -> FileResponse:
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404)
            return FileResponse(frontend_dist / "index.html")

    @application.exception_handler(AppError)
    async def handle_app_error(request: Request, error: AppError) -> ErrorJSONResponse:
        return error_response(error, request_id=request.state.request_id)

    return application


app = create_app()
