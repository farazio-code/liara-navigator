import pytest
from app.domain.errors import AppError, ErrorCode
from app.security.rate_limit import MemoryRateLimiter


def test_rate_limit_is_bounded_and_recovers_after_the_window() -> None:
    now = [100.0]
    limiter = MemoryRateLimiter(clock=lambda: now[0])
    limiter.check("session-1", "turn", limit=2, window_seconds=60)
    limiter.check("session-1", "turn", limit=2, window_seconds=60)

    with pytest.raises(AppError) as caught:
        limiter.check("session-1", "turn", limit=2, window_seconds=60)
    assert caught.value.code == ErrorCode.AUTH_RATE_LIMITED

    now[0] = 161.0
    limiter.check("session-1", "turn", limit=2, window_seconds=60)
