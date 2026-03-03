"""Base classes and utilities for resource batching."""

import asyncio
from collections.abc import Coroutine
from typing import Any


async def gather_with_limit[T](
    coros: list[Coroutine[Any, Any, T]], concurrency: int = 10
) -> list[T]:
    """Run coroutines concurrently with a semaphore limit."""
    sem = asyncio.Semaphore(concurrency)

    async def limited(coro: Coroutine[Any, Any, T]) -> T:
        async with sem:
            return await coro

    return await asyncio.gather(*(limited(c) for c in coros))
