from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from app.domain.errors import AppError, ErrorCode


class FakeLiaraClient:
    def __init__(self, fixture_path: Path | None = None) -> None:
        resolved_path = fixture_path or Path(__file__).with_name("fixtures") / "demo.json"
        self._payload: dict[str, Any] = json.loads(resolved_path.read_text(encoding="utf-8"))

    def platforms(self) -> list[dict[str, str]]:
        return list(self._payload["platforms"])

    def apps(self, *, user_id: str, platform: str) -> list[dict[str, str]]:
        apps = self._payload["users"].get(user_id, {}).get("apps", [])
        return [
            {
                "id": app["id"],
                "name": app["name"],
                "platform": app["platform"],
                "status": app["status"],
            }
            for app in apps
            if app["platform"] == platform
        ]

    def services(self, *, user_id: str, app_id: str) -> list[dict[str, str]]:
        app = self._find_app(user_id=user_id, app_id=app_id)
        return [
            {
                "id": service["id"],
                "name": service["name"],
                "kind": service["kind"],
                "status": service["status"],
            }
            for service in app["services"]
        ]

    def logs(
        self, *, user_id: str, service_id: str, limit: int
    ) -> tuple[list[dict[str, str]], bool]:
        service = self._find_service(user_id=user_id, service_id=service_id)
        lines: list[dict[str, str]] = service["logs"]
        return lines[-limit:], len(lines) > limit

    def _find_app(self, *, user_id: str, app_id: str) -> dict[str, Any]:
        for app in self._payload["users"].get(user_id, {}).get("apps", []):
            if app["id"] == app_id:
                return cast(dict[str, Any], app)
        raise AppError(ErrorCode.RESOURCE_NOT_ALLOWED)

    def _find_service(self, *, user_id: str, service_id: str) -> dict[str, Any]:
        for app in self._payload["users"].get(user_id, {}).get("apps", []):
            for service in app["services"]:
                if service["id"] == service_id:
                    return cast(dict[str, Any], service)
        raise AppError(ErrorCode.RESOURCE_NOT_ALLOWED)
