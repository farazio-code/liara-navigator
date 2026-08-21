from __future__ import annotations

from app.config import Settings
from app.main import create_app
from openapi_spec_validator import validate


def make_settings() -> Settings:
    return Settings(
        _env_file=None,
        APP_ENV="test",
        DATABASE_URL="postgresql+asyncpg://navigator:navigator@localhost:5432/navigator",
        SESSION_HMAC_SECRET="s" * 32,
        AVALAI_API_KEY="test-api-key-not-a-real-secret",
    )


def test_runtime_openapi_has_foundational_paths_and_strict_error_schema() -> None:
    schema = create_app(make_settings()).openapi()
    validate(schema)

    assert schema["openapi"].startswith("3.1")
    assert {"/api/v1/sessions", "/api/v1/health/live"} <= set(schema["paths"])
    session_response = schema["paths"]["/api/v1/sessions"]["post"]["responses"]["201"]
    assert "application/json" in session_response["content"]
    error_schema = schema["components"]["schemas"]["ErrorResponse"]
    assert error_schema["additionalProperties"] is False
    assert set(error_schema["required"]) == {"code", "message", "request_id", "retryable"}
