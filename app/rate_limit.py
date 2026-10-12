import asyncio
import math
import time
from collections.abc import Callable


class FixedWindowRateLimiter:
    def __init__(
        self,
        limit: int,
        window_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._window_started = clock()
        self._requests = 0
        self._lock = asyncio.Lock()

    async def check(self) -> int | None:
        async with self._lock:
            now = self._clock()
            elapsed = now - self._window_started
            if elapsed >= self.window_seconds:
                self._window_started = now
                self._requests = 0

            if self._requests >= self.limit:
                remaining = self.window_seconds - (now - self._window_started)
                return max(1, math.ceil(remaining))

            self._requests += 1
            return None
