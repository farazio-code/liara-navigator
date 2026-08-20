from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings


VALID_ENV = {
    "APP_ENV": "test",
    "DATABASE_URL": "postgresql+asyncpg://navigator:navigator@localhost:5432/navigator",
    "SESSION_HMAC_SECRET": "a" * 32,
    "AVALAI_API_KEY": "test-api-key-not-a-real-secret",
}


def test_settings_require_runtime_secrets() -> None:
    with pytest.raises(ValidationError) as error:
        Settings(_env_file=None)

    messages = {item["loc"][0] for item in error.value.errors()}
    assert {"DATABASE_URL", "SESSION_HMAC_SECRET", "AVALAI_API_KEY"} <= messages


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("SESSION_HMAC_SECRET", "short"),
        ("SESSION_HMAC_SECRET", "change-me-in-production-change-me"),
        ("AI_BASE_URL", "http://api.avalai.ir/v1"),
    ],
)
def test_settings_reject_unsafe_values(field: str, value: str) -> None:
    values = VALID_ENV | {field: value}

    with pytest.raises(ValidationError):
        Settings(_env_file=None, **values)


def test_settings_accept_safe_explicit_values() -> None:
    settings = Settings(_env_file=None, **VALID_ENV)

    assert settings.APP_ENV == "test"
    assert settings.AI_BASE_URL.unicode_string() == "https://api.avalai.ir/v1"
    assert settings.AVALAI_API_KEY.get_secret_value() == VALID_ENV["AVALAI_API_KEY"]
