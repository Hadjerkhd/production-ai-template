import pytest

from app.rate_limit import FixedWindowRateLimiter


@pytest.mark.asyncio
async def test_fixed_window_limiter_resets_after_window():
    current_time = [0.0]
    limiter = FixedWindowRateLimiter(
        limit=1,
        window_seconds=30,
        clock=lambda: current_time[0],
    )

    assert await limiter.check() is None
    assert await limiter.check() == 30

    current_time[0] = 30.0
    assert await limiter.check() is None
