"""Unit tests for async consumers."""
from typing import TypeVar
from unittest.mock import AsyncMock

import pytest

from zephcast.aio.consumers import AsyncConsumerConfig, batch_consumer, consumer
from zephcast.aio.retry import AsyncRetryConfig
from zephcast.core.consumers import ExecutorType
from zephcast.testing.aio.mock_client import MockAsyncClient

T = TypeVar("T")


@pytest.fixture
def mock_queue_client() -> MockAsyncClient:
    client = MockAsyncClient(stream_name="test-stream", received_messages=[])
    return client


@pytest.fixture
async def mock_message_handler() -> AsyncMock:
    """Create a mock message handler."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_consumer_without_executor() -> None:
    """Test consumer without executor."""
    client = MockAsyncClient(stream_name="test-stream", received_messages=["1", "2"])

    handler = AsyncMock()
    decorated = consumer(client)(handler)

    async with client:
        await decorated()

    assert handler.call_count == 2
    handler.assert_any_call("1")
    handler.assert_any_call("2")


@pytest.mark.asyncio
async def test_consumer_with_thread_executor() -> None:
    """Test consumer with thread executor."""
    mock_queue_client = MockAsyncClient(stream_name="test-stream", received_messages=["1", "2"])

    handler = AsyncMock()
    config = AsyncConsumerConfig(executor_type=ExecutorType.THREAD, num_workers=2)

    decorated = consumer(mock_queue_client, config)(handler)

    async with mock_queue_client:
        await decorated()

    assert handler.call_count == 2
    handler.assert_any_call("1")
    handler.assert_any_call("2")


@pytest.mark.asyncio
async def test_consumer_with_retry() -> None:
    """Test consumer with retry configuration."""
    mock_queue_client = MockAsyncClient(stream_name="test-stream", received_messages=["1"])

    handler = AsyncMock()
    handler.side_effect = [ValueError("First attempt fails"), None]

    config = AsyncConsumerConfig(retry=AsyncRetryConfig(max_retries=1, retry_sleep=0.1))

    decorated = consumer(mock_queue_client, config)(handler)

    async with mock_queue_client:
        await decorated()

    assert handler.call_count == 2
    handler.assert_called_with("1")


@pytest.mark.asyncio
async def test_batch_consumer_basic() -> None:
    """Test basic batch consumer functionality."""
    mock_queue_client = MockAsyncClient(
        stream_name="test-stream", received_messages=[str(i) for i in range(15)]
    )

    handler = AsyncMock()
    config = AsyncConsumerConfig(batch_size=10)

    decorated = batch_consumer(mock_queue_client, config)(handler)

    async with mock_queue_client:
        await decorated()

    assert handler.call_count == 1
    handler.assert_called_once_with([str(i) for i in range(10)])


@pytest.mark.asyncio
async def test_batch_consumer_with_executor() -> None:
    """Test batch consumer with thread executor."""
    mock_queue_client = MockAsyncClient(
        stream_name="test-stream", received_messages=[str(i) for i in range(10)]
    )

    handler = AsyncMock()
    config = AsyncConsumerConfig(batch_size=10, executor_type=ExecutorType.THREAD, num_workers=2)

    decorated = batch_consumer(mock_queue_client, config)(handler)

    async with mock_queue_client:
        await decorated()

    assert handler.call_count == 1
    handler.assert_called_once_with([str(i) for i in range(10)])


@pytest.mark.asyncio
async def test_batch_consumer_with_retry(mock_message_handler: AsyncMock) -> None:
    """Test batch consumer with retry configuration."""
    mock_queue_client = MockAsyncClient(
        stream_name="test-stream", received_messages=[str(i) for i in range(10)]
    )

    handler = AsyncMock()
    handler.side_effect = [ValueError("First attempt fails"), None]

    config = AsyncConsumerConfig(batch_size=10, retry=AsyncRetryConfig(max_retries=1, retry_sleep=0.1))

    decorated = batch_consumer(mock_queue_client, config)(handler)

    async with mock_queue_client:
        await decorated()

    assert handler.call_count == 2
    expected_batch = [str(i) for i in range(10)]
    handler.assert_called_with(expected_batch)
