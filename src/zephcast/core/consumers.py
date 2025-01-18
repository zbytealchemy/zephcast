"""Decorators for message consumers."""

import asyncio
import functools
import logging

from collections.abc import Awaitable
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional, TypeVar

from .retry import RetryConfig, retry

logger = logging.getLogger(__name__)

T = TypeVar("T")
AsyncMessageHandler = Callable[[T], Awaitable[Any]]
SyncMessageHandler = Callable[[T], Any]


class ExecutorType(Enum):
    """Executor types."""
    THREAD = "thread"
    PROCESS = "process"


@dataclass
class ConsumerConfig:
    """Configuration for consumer decorator."""
    retry: Optional[RetryConfig] = None
    batch_size: int = 1
    batch_timeout: float = 1.0
    executor_type: Optional[ExecutorType] = None
    num_workers: int = 1
    auto_ack: bool = False


def get_executor(executor_type: Optional[ExecutorType], max_workers: int) -> Optional[Executor]:
    """Create an executor based on the configuration."""
    if executor_type == ExecutorType.THREAD:
        return ThreadPoolExecutor(max_workers=max_workers)
    if executor_type == ExecutorType.PROCESS:
        return ProcessPoolExecutor(max_workers=max_workers)
    return None


def async_consumer(queue_client: Any, config: Optional[ConsumerConfig] = None) -> None:
    """Decorator for asynchronous message consumers."""
    config = config or ConsumerConfig()

    def decorator(func: AsyncMessageHandler[T]) -> Callable[[], Awaitable[None]]:
        if config.retry:
            func = retry(config.retry)(func)

        @functools.wraps(func)
        async def consume() -> None:
            """Automatically fetch messages and process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            try:
                async for message in queue_client.receive():
                    if executor:
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(executor, func, message)
                    else:
                        await func(message)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        return consume

    return decorator  # type: ignore


def async_batch_consumer(queue_client: Any, config: Optional[ConsumerConfig] = None) -> None:
    """Decorator for asynchronous batch message consumers."""
    config = config or ConsumerConfig(batch_size=10)

    def decorator(func: AsyncMessageHandler[list[T]]) -> Callable[[], Awaitable[None]]:
        if config.retry:
            func = retry(config.retry)(func)

        @functools.wraps(func)
        async def consume() -> None:
            """Automatically fetch and batch messages, then process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            buffer = []
            try:
                async for message in queue_client.receive():
                    buffer.append(message)
                    if len(buffer) >= config.batch_size:
                        if executor:
                            loop = asyncio.get_running_loop()
                            await loop.run_in_executor(executor, func, buffer)
                        else:
                            await func(buffer)
                        buffer.clear()
                if buffer:
                    if executor:
                        loop = asyncio.get_running_loop()
                        await loop.run_in_executor(executor, func, buffer)
                    else:
                        await func(buffer)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        return consume

    return decorator  # type: ignore


def sync_consumer(queue_client: Any, config: Optional[ConsumerConfig] = None) -> None:
    """Decorator for synchronous message consumers."""
    config = config or ConsumerConfig()

    def decorator(func: SyncMessageHandler[T]) -> Callable[[], None]:
        if config.retry:
            func = retry(config.retry)(func)

        @functools.wraps(func)
        def consume() -> None:
            """Automatically fetch messages and process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            try:
                for message in queue_client.receive():
                    if executor:
                        executor.submit(func, message).result()
                    else:
                        func(message)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        return consume

    return decorator  # type: ignore


def sync_batch_consumer(queue_client: Any, config: Optional[ConsumerConfig] = None) -> None:
    """Decorator for synchronous batch message consumers."""
    config = config or ConsumerConfig(batch_size=10)

    def decorator(func: SyncMessageHandler[list[T]]) -> Callable[[], None]:
        if config.retry:
            func = retry(config.retry)(func)

        @functools.wraps(func)
        def consume() -> None:
            """Automatically fetch and batch messages, then process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            buffer = []
            try:
                for message in queue_client.receive():
                    buffer.append(message)
                    if len(buffer) >= config.batch_size:
                        if executor:
                            executor.submit(func, buffer).result()
                        else:
                            func(buffer)
                        buffer.clear()
                if buffer:
                    if executor:
                        executor.submit(func, buffer).result()
                    else:
                        func(buffer)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        return consume

    return decorator  # type: ignore
