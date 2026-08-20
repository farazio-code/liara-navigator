from __future__ import annotations

import asyncio
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import TypeVar


ResultT = TypeVar("ResultT")


class BoundedExecutor:
    def __init__(self, *, max_workers: int) -> None:
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="navigator-cpu",
        )
        self._capacity = asyncio.Semaphore(max_workers * 2)

    async def run(self, function: Callable[..., ResultT], *args: object) -> ResultT:
        async with self._capacity:
            loop = asyncio.get_running_loop()
            return await loop.run_in_executor(self._executor, partial(function, *args))

    async def aclose(self) -> None:
        self._executor.shutdown(wait=True, cancel_futures=True)
