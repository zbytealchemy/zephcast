"""Retry functionality for synchronous operations."""
import functools

from time import sleep
from typing import Any, Callable, Optional, TypeVar

from zephcast.core.retry import RetryConfig

T = TypeVar("T")


class SyncRetryConfig(RetryConfig):
    """Configuration for sync retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        retry_sleep: float = 1.0,
        backoff_factor: float = 2.0,
        exceptions: tuple[type[Exception], ...] = (Exception,),
        condition: Optional[Callable[[Any], bool]] = None,
        on_retry: Optional[Callable[[int, Exception], None]] = None,
    ) -> None:
        """Initialize sync retry configuration."""
        super().__init__(
            max_retries=max_retries,
            retry_sleep=retry_sleep,
            backoff_factor=backoff_factor,
            exceptions=exceptions,
        )
        self.condition = condition
        self.on_retry = on_retry


def retry(config: SyncRetryConfig) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator for adding retry behavior to synchronous functions."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            sleep_time = config.retry_sleep

            for attempt in range(config.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if config.condition and not config.condition(result):
                        raise ValueError("Retry condition not met")
                    return result
                except config.exceptions as exc:
                    last_exception = exc
                    if attempt < config.max_retries:
                        if config.on_retry:
                            config.on_retry(attempt + 1, exc)
                        sleep(sleep_time)
                        sleep_time *= config.backoff_factor
                    else:
                        raise

            assert last_exception is not None  # for type checker
            raise last_exception

        return wrapper

    return decorator
