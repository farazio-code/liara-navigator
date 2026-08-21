from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable

from app.domain.errors import AppError, ErrorCode


class MemoryRateLimiter:
    def __init__(self, *, clock: Callable[[], float] = time.monotonic) -> None:
        self._clock = clock
        self._buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def check(self, key: str, action: str, *, limit: int, window_seconds: int) -> None:
        now = self._clock()
        bucket = self._buckets[(key, action)]
        cutoff = now - window_seconds
        while bucket and bucket[0] <= cutoff:
            bucket.popleft()
        if len(bucket) >= limit:
            raise AppError(ErrorCode.AUTH_RATE_LIMITED)
        bucket.append(now)
