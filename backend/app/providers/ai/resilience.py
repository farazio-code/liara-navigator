from __future__ import annotations

import time
from collections.abc import Callable

from app.domain.errors import AppError, ErrorCode


class CircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_seconds: float = 30,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._clock = clock
        self._failures = 0
        self._open_until = 0.0

    def check(self) -> None:
        if self._clock() < self._open_until:
            raise AppError(ErrorCode.AI_RATE_LIMITED)

    def success(self) -> None:
        self._failures = 0
        self._open_until = 0.0

    def failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._open_until = self._clock() + self._recovery_seconds
