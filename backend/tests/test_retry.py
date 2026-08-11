"""Tests for retry-with-backoff (WBS 1.1.4, part 1/2)."""
from __future__ import annotations

import pytest

from app.providers.base import ProviderConfigError, ProviderResponseError
from app.providers.retry import RetryPolicy, retry_async


async def _no_sleep(_s: float) -> None:
    return None


def test_delay_grows_exponentially_and_caps():
    p = RetryPolicy(base_delay=1.0, factor=2.0, max_delay=5.0)
    assert p.delay_for(1) == 1.0
    assert p.delay_for(2) == 2.0
    assert p.delay_for(3) == 4.0
    assert p.delay_for(10) == 5.0  # capped


@pytest.mark.asyncio
async def test_succeeds_after_transient_failures():
    calls = {"n": 0}

    async def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ProviderResponseError("temporary")
        return "ok"

    result = await retry_async(flaky, RetryPolicy(max_attempts=3), sleep=_no_sleep)
    assert result == "ok"
    assert calls["n"] == 3


@pytest.mark.asyncio
async def test_raises_after_exhausting_attempts():
    async def always_fails():
        raise ProviderResponseError("down")

    with pytest.raises(ProviderResponseError):
        await retry_async(always_fails, RetryPolicy(max_attempts=2), sleep=_no_sleep)


@pytest.mark.asyncio
async def test_non_transient_error_not_retried():
    calls = {"n": 0}

    async def bad_config():
        calls["n"] += 1
        raise ProviderConfigError("no key")

    with pytest.raises(ProviderConfigError):
        await retry_async(bad_config, RetryPolicy(max_attempts=3), sleep=_no_sleep)
    assert calls["n"] == 1  # not retried
