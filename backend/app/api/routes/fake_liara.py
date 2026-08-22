from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, ConfigDict

PlatformId = Literal[
    "angular",
    "django",
    "docker",
    "dotnet",
    "flask",
    "go",
    "laravel",
    "nextjs",
    "nodejs",
    "php",
    "python",
    "react",
    "static",
    "vue",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PlatformSummary(StrictModel):
    id: PlatformId
    label: str


class PlatformList(StrictModel):
    platforms: list[PlatformSummary]


class AppSummary(StrictModel):
    ref: str
    name: str
    platform: PlatformId
    status: Literal["running", "stopped", "degraded"]


class AppList(StrictModel):
    apps: list[AppSummary]


class ServiceSummary(StrictModel):
    ref: str
    name: str
    kind: Literal["web", "worker", "cron"]
    status: Literal["healthy", "degraded", "stopped"]


class ServiceList(StrictModel):
    services: list[ServiceSummary]


class LogLine(StrictModel):
    timestamp: datetime
    stream: Literal["stdout", "stderr"]
    message: str


class LogBatch(StrictModel):
    service_ref: str
    lines: list[LogLine]
    truncated: bool
    fetched_at: datetime


router = APIRouter(prefix="/fake-liara", tags=["Fake Liara"])


def _session_id(request: Request) -> str:
    session = request.app.state.session_vault.get(request.cookies.get("ln_session"))
    return str(session.session_id)


@router.get("/platforms", response_model=PlatformList)
async def list_platforms(request: Request) -> PlatformList:
    _session_id(request)
    return PlatformList(platforms=request.app.state.fake_liara.platforms())


@router.get("/apps", response_model=AppList)
async def list_apps(request: Request, platform: PlatformId) -> AppList:
    session_id = _session_id(request)
    apps = request.app.state.fake_liara.apps(user_id="demo-user", platform=platform)
    return AppList(
        apps=[
            AppSummary(
                ref=request.app.state.session_vault.bind_resource(
                    session_id, kind="app", resource_id=app["id"]
                ),
                name=app["name"],
                platform=app["platform"],
                status=app["status"],
            )
            for app in apps
        ]
    )


@router.get("/apps/{app_ref}/services", response_model=ServiceList)
async def list_services(request: Request, app_ref: str) -> ServiceList:
    session_id = _session_id(request)
    app_id = request.app.state.session_vault.resolve_resource(
        session_id, app_ref, kind="app"
    )
    services = request.app.state.fake_liara.services(user_id="demo-user", app_id=app_id)
    return ServiceList(
        services=[
            ServiceSummary(
                ref=request.app.state.session_vault.bind_resource(
                    session_id, kind="service", resource_id=service["id"]
                ),
                name=service["name"],
                kind=service["kind"],
                status=service["status"],
            )
            for service in services
        ]
    )


@router.get("/services/{service_ref}/logs", response_model=LogBatch)
async def get_logs(
    request: Request,
    service_ref: str,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
) -> LogBatch:
    session_id = _session_id(request)
    service_id = request.app.state.session_vault.resolve_resource(
        session_id, service_ref, kind="service"
    )
    lines, truncated = request.app.state.fake_liara.logs(
        user_id="demo-user", service_id=service_id, limit=limit
    )
    return LogBatch(
        service_ref=service_ref,
        lines=lines,
        truncated=truncated,
        fetched_at=datetime.fromisoformat("2026-08-21T18:46:00+00:00"),
    )
