from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from app.api.dependencies import BoundedExecutor
from app.api.errors import ErrorJSONResponse, error_response
from app.api.middleware import SecurityMiddleware
from app.api.routes import fake_liara, health, sessions
from app.config import Settings
from app.domain.errors import AppError
from app.providers.fake_liara.client import FakeLiaraClient
from app.security.session_vault import MemorySessionVault


def create_app(
    settings: Settings | None = None,
    *,
    executor: BoundedExecutor | None = None,
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
    application.include_router(health.router, prefix="/api/v1")

    @application.exception_handler(AppError)
    async def handle_app_error(request: Request, error: AppError) -> ErrorJSONResponse:
        return error_response(error, request_id=request.state.request_id)

    return application


app = create_app()
