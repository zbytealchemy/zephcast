"""Decorators for message consumers."""

from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .retry import RetryConfig


class ExecutorType(Enum):
    """Executor types."""

    THREAD = "thread"
    PROCESS = "process"


@dataclass
class ConsumerConfig:
    """Base configuration for consumer decorators."""

    batch_size: int = 1
    batch_timeout: float = 1.0
    executor_type: Optional[ExecutorType] = None
    num_workers: int = 1
    auto_ack: bool = True
    max_messages: Optional[int] = None
    retry: Optional[RetryConfig] = None


def get_executor(executor_type: Optional[ExecutorType], max_workers: int) -> Optional[Executor]:
    """Create an executor based on the configuration."""
    if executor_type == ExecutorType.THREAD:
        return ThreadPoolExecutor(max_workers=max_workers)
    if executor_type == ExecutorType.PROCESS:
        return ProcessPoolExecutor(max_workers=max_workers)
    return None
