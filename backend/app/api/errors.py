from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from fastapi.responses import JSONResponse

from app.api.schemas import ErrorResponse
from app.domain.errors import AppError, ErrorCode


@dataclass(frozen=True, slots=True)
class ErrorPolicy:
    status_code: int
    message: str
    retryable: bool


ERROR_POLICIES: Final[dict[ErrorCode, ErrorPolicy]] = {
    ErrorCode.AUTH_INVALID: ErrorPolicy(401, "توکن لیارا معتبر نیست.", False),
    ErrorCode.AUTH_RATE_LIMITED: ErrorPolicy(
        429, "تعداد تلاش‌ها بیش از حد مجاز است.", True  # noqa: RUF001
    ),
    ErrorCode.SESSION_INVALID: ErrorPolicy(401, "نشست معتبر نیست یا منقضی شده است.", False),
    ErrorCode.CSRF_INVALID: ErrorPolicy(403, "اعتبار درخواست تأیید نشد.", False),
    ErrorCode.LIARA_TIMEOUT: ErrorPolicy(502, "پاسخ لیارا بیش از حد طول کشید.", True),
    ErrorCode.LIARA_UNAVAILABLE: ErrorPolicy(502, "سرویس لیارا موقتاً در دسترس نیست.", True),
    ErrorCode.POLICY_DENIED: ErrorPolicy(403, "این بررسی طبق سیاست ایمنی مجاز نیست.", False),
    ErrorCode.RESOURCE_NOT_ALLOWED: ErrorPolicy(404, "منبع در این نشست در دسترس نیست.", False),
    ErrorCode.AI_TIMEOUT: ErrorPolicy(504, "پاسخ سرویس هوش مصنوعی بیش از حد طول کشید.", True),
    ErrorCode.AI_RATE_LIMITED: ErrorPolicy(429, "ظرفیت سرویس هوش مصنوعی موقتاً پر است.", True),
    ErrorCode.AI_INVALID_OUTPUT: ErrorPolicy(502, "پاسخ قابل‌اعتماد تولید نشد.", True),
    ErrorCode.RETRIEVAL_EMPTY: ErrorPolicy(404, "منبع رسمی مرتبطی پیدا نشد.", False),
    ErrorCode.CITATION_CORE_FAILED: ErrorPolicy(422, "پاسخ قطعی در منابع رسمی پیدا نشد.", False),
    ErrorCode.SNAPSHOT_INCOMPATIBLE: ErrorPolicy(503, "پایگاه دانش آماده نیست.", False),
    ErrorCode.IDEMPOTENCY_CONFLICT: ErrorPolicy(
        409, "شناسه درخواست با محتوای دیگری استفاده شده است.", False
    ),
    ErrorCode.VALIDATION_FAILED: ErrorPolicy(422, "دادهٔ درخواست معتبر نیست.", False),
    ErrorCode.REQUEST_NOT_FOUND: ErrorPolicy(404, "درخواست موردنظر پیدا نشد.", False),
    ErrorCode.SOURCE_NOT_FOUND: ErrorPolicy(404, "منبع موردنظر پیدا نشد.", False),
    ErrorCode.INTERNAL_ERROR: ErrorPolicy(500, "خطای داخلی رخ داد.", False),
}


class ErrorJSONResponse(JSONResponse):
    model: ErrorResponse

    def __init__(self, *, status_code: int, model: ErrorResponse) -> None:
        self.model = model
        super().__init__(status_code=status_code, content=model.model_dump(mode="json"))


def error_response(error: Exception, *, request_id: str) -> ErrorJSONResponse:
    code = error.code if isinstance(error, AppError) else ErrorCode.INTERNAL_ERROR
    policy = ERROR_POLICIES[code]
    model = ErrorResponse(
        code=code,
        message=policy.message,
        request_id=request_id,
        retryable=policy.retryable,
    )
    return ErrorJSONResponse(status_code=policy.status_code, model=model)
