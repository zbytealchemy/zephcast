"""Synchronous consumer decorators."""

import functools

from dataclasses import dataclass
from typing import Any, Callable, Optional, TypeVar

from zephcast.core.consumers import ConsumerConfig, get_executor
from zephcast.sync.retry import SyncRetryConfig

T = TypeVar("T")
SyncMessageHandler = Callable[[T], Any]


@dataclass
class SyncConsumerConfig(ConsumerConfig):
    """Configuration for sync consumer decorator."""

    retry: Optional[SyncRetryConfig] = None


def consumer(
    queue_client: Any, config: SyncConsumerConfig | None = None
) -> Callable[[SyncMessageHandler[T]], Callable[[], None]]:
    """Decorator for synchronous message consumers."""
    config = config or SyncConsumerConfig()

    def decorator(func: SyncMessageHandler[T]) -> Callable[[], None]:
        if config.retry:
            from zephcast.sync.retry import retry

            func = retry(config.retry)(func)

        @functools.wraps(func)
        def consume() -> None:
            """Automatically fetch messages and process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            processed = 0
            try:
                for message in queue_client.receive():
                    if config.max_messages is not None and processed >= config.max_messages:
                        break
                    if executor:
                        executor.submit(func, message).result()
                    else:
                        func(message)
                    processed += 1
            finally:
                if executor:
                    executor.shutdown(wait=False)

        return consume

    return decorator


def batch_consumer(
    queue_client: Any, config: SyncConsumerConfig | None = None
) -> Callable[[SyncMessageHandler[list[T]]], Callable[[], None]]:
    """Decorator for synchronous batch message consumers."""
    config = config or SyncConsumerConfig(batch_size=10)

    def decorator(func: SyncMessageHandler[list[T]]) -> Callable[[], None]:
        if config.retry:
            from zephcast.sync.retry import retry

            func = retry(config.retry)(func)

        @functools.wraps(func)
        def consume() -> None:
            """Automatically fetch and batch messages, then process them."""
            executor = get_executor(config.executor_type, config.num_workers)
            buffer = []
            processed = 0
            try:
                for message in queue_client.receive():
                    if config.max_messages and processed >= config.max_messages:
                        break
                    buffer.append(message)
                    processed += 1
                    if len(buffer) >= config.batch_size:
                        batch = buffer[:]
                        buffer.clear()
                        if executor:
                            executor.submit(func, batch).result()
                        else:
                            func(batch)

                # Process any remaining messages in the buffer
                if buffer:
                    if executor:
                        executor.submit(func, buffer).result()
                    else:
                        func(buffer)
            finally:
                if executor:
                    executor.shutdown(wait=False)

        return consume

    return decorator
