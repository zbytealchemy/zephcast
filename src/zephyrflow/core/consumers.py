import asyncio
import functools
import logging
import time

from collections.abc import Awaitable, Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Optional, TypeVar, Union, cast

from .retry import RetryConfig, retry

logger = logging.getLogger(__name__)

T = TypeVar("T")
MessageHandler = Callable[[T], Any]
AsyncMessageHandler = Callable[[T], Awaitable[Any]]
ExecutorType = Union[ThreadPoolExecutor, ProcessPoolExecutor]


@dataclass
class ConsumerConfig:
    """Configuration for consumer decorator.

    Args:
        retry: Retry configuration
        executor_type: Executor type ("thread" or "process")
        num_workers: Number of workers
        batch_size: Batch size
        batch_timeout: Batch timeout in seconds
        auto_ack: Auto ack messages
        dead_letter_queue: Dead letter queue name
    """

    retry: Optional[RetryConfig] = None

    executor_type: Optional[str] = None  # "thread" or "process"
    num_workers: int = 1

    batch_size: int = 1
    batch_timeout: float = 1.0

    auto_ack: bool = True
    dead_letter_queue: Optional[str] = None


def consumer(
    config: Optional[ConsumerConfig] = None,
    **kwargs: Any,
) -> Callable[[MessageHandler[T]], MessageHandler[T]]:
    """
    Decorator for message consumers.

    Args:
        config: Consumer configuration
        **kwargs: Override configuration parameters

    Returns:
        Decorated message handler
    """
    if config is None:
        config = ConsumerConfig()

    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    def get_executor() -> Optional[ExecutorType]:
        if config.executor_type == "thread":
            return ThreadPoolExecutor(max_workers=config.num_workers)
        elif config.executor_type == "process":
            return ProcessPoolExecutor(max_workers=config.num_workers)
        return None

    def decorator(
        func: MessageHandler[T],
    ) -> MessageHandler[T]:
        """Decorate the message handler."""
        if config.retry:
            func = retry(config=config.retry)(func)

        @functools.wraps(func)
        def sync_wrapper(message: T) -> Any:
            executor = get_executor()
            try:
                if executor:
                    return executor.submit(func, message).result()
                return func(message)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        @functools.wraps(func)
        async def async_wrapper(message: T) -> Any:
            executor = get_executor()
            try:
                if executor:
                    loop = asyncio.get_running_loop()
                    return await loop.run_in_executor(executor, func, message)
                if asyncio.iscoroutinefunction(func):
                    return await func(message)
                return func(message)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        if asyncio.iscoroutinefunction(func):
            return cast(MessageHandler[T], async_wrapper)
        return cast(MessageHandler[T], sync_wrapper)

    return decorator


def batch_consumer(
    config: Optional[ConsumerConfig] = None,
    **kwargs: Any,
) -> Callable[[MessageHandler[list[T]]], MessageHandler[list[T]]]:
    """
    Decorator for batch message consumers.

    Args:
        config: Consumer configuration
        **kwargs: Override configuration parameters

    Returns:
        Decorated batch message handler
    """
    if config is None:
        config = ConsumerConfig()

    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

    def decorator(
        func: MessageHandler[list[T]],
    ) -> MessageHandler[list[T]]:
        if config.retry:
            func = retry(config=config.retry)(func)

        @functools.wraps(func)
        async def async_wrapper(messages: list[T]) -> Any:
            if len(messages) >= config.batch_size:
                if asyncio.iscoroutinefunction(func):
                    return await func(messages)
                return func(messages)

            await asyncio.sleep(config.batch_timeout)
            if asyncio.iscoroutinefunction(func):
                return await func(messages)
            return func(messages)

        @functools.wraps(func)
        def sync_wrapper(messages: list[T]) -> Any:
            if len(messages) >= config.batch_size:
                return func(messages)

            time.sleep(config.batch_timeout)
            return func(messages)

        if asyncio.iscoroutinefunction(func):
            return cast(MessageHandler[list[T]], async_wrapper)
        return cast(MessageHandler[list[T]], sync_wrapper)

    return decorator
