from __future__ import annotations

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


async def create_session(client: httpx.AsyncClient) -> None:
    response = await client.post("/api/v1/sessions")
    assert response.status_code == 201


@pytest.mark.asyncio
async def test_lists_platforms_apps_services_and_bounded_logs() -> None:
    app = create_app(make_settings())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        await create_session(client)

        platforms = await client.get("/api/v1/fake-liara/platforms")
        assert platforms.status_code == 200
        assert {item["id"] for item in platforms.json()["platforms"]} >= {
            "django",
            "dotnet",
        }

        apps = await client.get("/api/v1/fake-liara/apps", params={"platform": "django"})
        assert apps.status_code == 200
        selected_app = apps.json()["apps"][0]
        assert set(selected_app) == {"ref", "name", "platform", "status"}
        assert "app_" not in selected_app["ref"]

        services = await client.get(
            f"/api/v1/fake-liara/apps/{selected_app['ref']}/services"
        )
        assert services.status_code == 200
        service = services.json()["services"][0]
        assert set(service) == {"ref", "name", "kind", "status"}

        logs = await client.get(
            f"/api/v1/fake-liara/services/{service['ref']}/logs",
            params={"limit": 2},
        )
        assert logs.status_code == 200
        payload = logs.json()
        assert payload["service_ref"] == service["ref"]
        assert len(payload["lines"]) == 2
        assert payload["truncated"] is True
        assert all(
            set(line) == {"timestamp", "stream", "message"} for line in payload["lines"]
        )


@pytest.mark.asyncio
async def test_resource_references_are_session_scoped() -> None:
    app = create_app(make_settings())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as owner,
        httpx.AsyncClient(transport=transport, base_url="http://test") as stranger,
    ):
        await create_session(owner)
        app_ref = (
            await owner.get("/api/v1/fake-liara/apps", params={"platform": "django"})
        ).json()["apps"][0]["ref"]
        await create_session(stranger)
        response = await stranger.get(f"/api/v1/fake-liara/apps/{app_ref}/services")

    assert response.status_code == 404
    assert response.json()["code"] == "RESOURCE_NOT_ALLOWED"


@pytest.mark.asyncio
async def test_rejects_unknown_platform_and_out_of_range_log_limit() -> None:
    app = create_app(make_settings())
    transport = httpx.ASGITransport(app=app)
    async with (
        app.router.lifespan_context(app),
        httpx.AsyncClient(transport=transport, base_url="http://test") as client,
    ):
        await create_session(client)
        unknown = await client.get(
            "/api/v1/fake-liara/apps", params={"platform": "wordpress"}
        )
        invalid_limit = await client.get(
            "/api/v1/fake-liara/services/not-a-ref/logs", params={"limit": 501}
        )

    assert unknown.status_code == 422
    assert invalid_limit.status_code == 422
