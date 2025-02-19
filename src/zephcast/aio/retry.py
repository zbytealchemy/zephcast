"""Retry functionality for asynchronous operations."""

import asyncio
import functools

from collections.abc import Coroutine
from typing import Any, Callable, Optional, TypeVar

from typing_extensions import ParamSpec

from zephcast.core.retry import RetryConfig

T = TypeVar("T")
R = TypeVar("R")


class AsyncRetryConfig(RetryConfig):
    """Configuration for async retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_sleep: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        condition: Optional[Callable[[Any], bool]] = None,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
    ) -> None:
        """Initialize async retry configuration."""
        super().__init__(
            max_retries=max_retries,
            retry_sleep=retry_sleep,
            backoff_factor=backoff_factor,
            exceptions=exceptions,
        )
        self.condition = condition
        self.on_retry = on_retry


P = ParamSpec("P")


def retry(
    config: AsyncRetryConfig,
) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
    """Decorator for adding retry behavior to asynchronous functions."""

    def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> R:
            last_exception = None
            sleep_time = config.retry_sleep

            for attempt in range(config.max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    if config.condition and not config.condition(result):
                        raise ValueError("Retry condition not met")
                    return result
                except config.exceptions as exc:
                    last_exception = exc
                    if attempt < config.max_retries:
                        if config.on_retry:
                            config.on_retry(attempt + 1, exc)
                        # Add small random jitter (±10% of sleep time)
                        jittered_sleep = sleep_time * (1 + (asyncio.get_event_loop().time() % 0.2 - 0.1))
                        await asyncio.sleep(jittered_sleep)
                        sleep_time *= config.backoff_factor
                    else:
                        raise

            assert last_exception is not None  # for type checker
            raise last_exception

        return wrapper

    return decorator
