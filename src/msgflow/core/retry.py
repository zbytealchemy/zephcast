"""Retry decorator for sync and async functions."""

import asyncio
import functools
import logging

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any, Optional, TypeVar, Union, cast

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])

logger = logging.getLogger(__name__)


@dataclass
class RetryConfig:
    max_retries: int = 3
    retry_sleep: float = 1.0
    backoff_factor: float = 2.0
    exceptions: Optional[Sequence[type[Exception]]] = None
    condition: Optional[Callable[[Any], bool]] = None
    on_retry: Optional[Callable[[int, Exception], None]] = None


async def _async_sleep(duration: float) -> None:
    await asyncio.sleep(duration)


def _sync_sleep(duration: float) -> None:
    import time

    time.sleep(duration)


def _should_retry(e: Exception, config: RetryConfig) -> bool:
    if not config.exceptions:
        return True
    return isinstance(e, tuple(config.exceptions))


def _handle_retry(retries: int, e: Exception, func_name: str, config: RetryConfig) -> None:
    if config.on_retry:
        config.on_retry(retries, e)
    logger.warning(
        "Retry %d/%d for %s: %s",
        retries,
        config.max_retries,
        func_name,
        str(e),
    )


async def _retry_async(
    func: Callable[..., Any], args: tuple, kwargs: dict, config: RetryConfig
) -> Any:
    retries = 0
    sleep_time = config.retry_sleep

    while True:
        try:
            result = await func(*args, **kwargs)
            if config.condition and not config.condition(result):
                raise ValueError("Retry condition not met")
            return result
        except Exception as e:
            if not _should_retry(e, config):
                raise
            retries += 1
            if retries > config.max_retries:
                raise
            _handle_retry(retries, e, func.__name__, config)
            await _async_sleep(sleep_time)
            sleep_time *= config.backoff_factor


def _retry_sync(func: Callable[..., Any], args: tuple, kwargs: dict, config: RetryConfig) -> Any:
    retries = 0
    sleep_time = config.retry_sleep

    while True:
        try:
            result = func(*args, **kwargs)
            if config.condition and not config.condition(result):
                raise ValueError("Retry condition not met")
            return result
        except Exception as e:
            if not _should_retry(e, config):
                raise
            retries += 1
            if retries > config.max_retries:
                raise
            _handle_retry(retries, e, func.__name__, config)
            _sync_sleep(sleep_time)
            sleep_time *= config.backoff_factor


def retry(config: RetryConfig) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if asyncio.iscoroutinefunction(func):
                return _retry_async(func, args, kwargs, config)
            return _retry_sync(func, args, kwargs, config)

        return cast(F, wrapper)

    return decorator


def with_retry(func: Optional[F] = None, *, config: RetryConfig) -> Union[F, Callable[[F], F]]:
    if func is None:
        return lambda f: retry(config=config)(f)
    return retry(config=config)(func)
