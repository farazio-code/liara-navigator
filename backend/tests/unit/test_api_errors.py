from __future__ import annotations

from uuid import UUID

from app.api.errors import error_response
from app.domain.errors import AppError, ErrorCode


def test_error_mapping_exposes_only_bounded_public_fields() -> None:
    secret = "liara-token-must-never-escape"
    response = error_response(
        AppError(
            code=ErrorCode.LIARA_UNAVAILABLE,
            internal_detail=f"upstream Authorization: Bearer {secret}",
        ),
        request_id="18cbbc27-ea6f-4e61-a4f4-297ecbb25937",
    )

    payload = response.body.decode()
    assert response.status_code == 502
    assert secret not in payload
    assert "Authorization" not in payload
    assert len(response.model.message) <= 240
    assert response.model.retryable is True
    assert UUID(str(response.model.request_id))


def test_internal_error_has_generic_non_retryable_message() -> None:
    response = error_response(
        RuntimeError("database password=should-not-leak"),
        request_id="bfe64694-72fe-4c70-8974-d54050daa9cc",
    )

    assert response.status_code == 500
    assert response.model.code is ErrorCode.INTERNAL_ERROR
    assert response.model.message == "خطای داخلی رخ داد."
    assert response.model.retryable is False
    assert "password" not in response.body.decode()
