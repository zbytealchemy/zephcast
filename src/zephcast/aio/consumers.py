"""Asynchronous consumer implementations."""

import asyncio
import functools
import logging

from collections.abc import Awaitable, Coroutine
from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

from zephcast.aio.retry import AsyncRetryConfig
from zephcast.core.consumers import ConsumerConfig, get_executor

logger = logging.getLogger(__name__)
T = TypeVar("T")
AsyncMessageHandler = Callable[[T], Coroutine[Any, Any, Any]]


@dataclass
class AsyncConsumerConfig(ConsumerConfig):
    """Configuration for async consumer decorator."""

    retry: Optional[AsyncRetryConfig] = None


def consumer(
    queue_client: Any, config: Optional[AsyncConsumerConfig] = None
) -> Callable[[AsyncMessageHandler[T]], Callable[[], Awaitable[None]]]:
    """Decorator for asynchronous message consumers."""
    config = config or AsyncConsumerConfig()

    def decorator(func: AsyncMessageHandler[T]) -> Callable[[], Awaitable[None]]:
        if config.retry:
            from .retry import retry

            func = retry(config.retry)(func)

        @functools.wraps(func)
        async def consume() -> None:
            """Automatically fetch messages and process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            try:
                async for message in queue_client.receive():
                    if executor:

                        def run_coro(coro: Any) -> Any:
                            return asyncio.run(coro)

                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(executor, run_coro, func(message))
                    else:
                        await func(message)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        return consume

    return decorator


def batch_consumer(
    queue_client: Any, config: Optional[ConsumerConfig] = None
) -> Callable[[AsyncMessageHandler[list[T]]], Callable[[], Awaitable[None]]]:
    """Decorator for asynchronous batch message consumers."""
    config = config or ConsumerConfig(batch_size=10)

    if config.retry and not isinstance(config.retry, AsyncRetryConfig):
        raise TypeError("Async consumers require AsyncRetryConfig")

    def decorator(func: AsyncMessageHandler[list[T]]) -> Callable[[], Awaitable[None]]:
        if config.retry:
            from .retry import retry

            func = retry(config.retry)(func)  # type: ignore

        @functools.wraps(func)
        async def consume() -> None:
            """Automatically fetch and batch messages, then process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            buffer = []
            try:
                async for message in queue_client.receive():
                    buffer.append(message)
                    if len(buffer) >= config.batch_size:
                        batch = buffer[:]
                        buffer.clear()
                        if executor:

                            def run_coro(coro: Any) -> Any:
                                return asyncio.run(coro)

                            loop = asyncio.get_running_loop()
                            await loop.run_in_executor(executor, run_coro, func(batch))
                        else:
                            await func(batch)
            finally:
                if executor:
                    executor.shutdown(wait=True)

        return consume

    return decorator
