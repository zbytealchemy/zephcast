"""Tests for synchronous consumers."""
import queue
import time

from zephcast.core.consumers import ExecutorType
from zephcast.sync.consumers import SyncConsumerConfig
from zephcast.sync.retry import SyncRetryConfig
from zephcast.testing.sync.mock_client import MockSyncClient

shared_queue: queue.Queue[str] = queue.Queue()


def process_message_handler(message: str) -> None:
    """Handler function for single message processing."""
    shared_queue.put(message)
    time.sleep(0.1)


def process_batch_handler(messages: list[str]) -> None:
    """Handler function for batch processing."""
    for msg in messages:
        shared_queue.put(msg)
        time.sleep(0.1)


def test_sync_consumer_basic() -> None:
    """Test basic synchronous consumer functionality."""
    client = MockSyncClient("test-stream", received_messages=["message1", "message2"])

    messages = []

    @client.consumer()
    def handle_message(message: str) -> None:
        messages.append(message)

    with client:
        handle_message()

    assert messages == ["message1", "message2"]


def test_sync_batch_consumer() -> None:
    """Test synchronous batch consumer functionality."""
    client = MockSyncClient("test-stream", received_messages=["message1", "message2", "message3"])

    batches = []
    config = SyncConsumerConfig(batch_size=2)

    @client.batch_consumer(config=config)
    def handle_batch(messages: list[str]) -> None:
        batches.append(messages)

    with client:
        handle_batch()

    assert len(batches) == 2
    assert batches[0] == ["message1", "message2"]
    assert batches[1] == ["message3"]


def test_sync_consumer_with_retry() -> None:
    """Test synchronous consumer with retry configuration."""
    client = MockSyncClient("test-stream", received_messages=["message1"])

    attempts = []
    retry_config = SyncRetryConfig(max_retries=2, retry_sleep=0.1)
    config = SyncConsumerConfig(retry=retry_config)

    @client.consumer(config=config)
    def handle_message(message: str) -> None:
        attempts.append(message)
        if len(attempts) <= 2:
            raise ValueError("Simulated failure")

    with client:
        handle_message()

    assert len(attempts) == 3
    assert all(attempt == "message1" for attempt in attempts)


def test_sync_batch_consumer_with_thread_executor() -> None:
    """Test synchronous batch consumer with thread executor."""
    while not shared_queue.empty():
        shared_queue.get()

    test_messages = ["message1", "message2", "message3", "message4"]
    client = MockSyncClient("test-stream", received_messages=test_messages.copy())

    config = SyncConsumerConfig(batch_size=2, executor_type=ExecutorType.THREAD, num_workers=2)

    @client.batch_consumer(config=config)
    def handle_batch(messages: list[str]) -> None:
        process_batch_handler(messages)

    with client:
        handle_batch()
        time.sleep(0.5)

    processed_messages: list[str] = []
    timeout = 5
    start_time = time.time()

    while len(processed_messages) < len(test_messages):
        if time.time() - start_time > timeout:
            break
        try:
            msg = shared_queue.get(timeout=0.1)
            processed_messages.append(msg)
        except queue.Empty:
            continue

    assert sorted(processed_messages) == sorted(test_messages)


def test_sync_consumer_error_handling() -> None:
    """Test error handling in synchronous consumer."""
    client = MockSyncClient("test-stream", received_messages=["message1", "message2"])

    processed = []
    errors = []

    @client.consumer()
    def handle_message(message: str) -> None:
        if message == "message2":
            raise ValueError("Test error")
        processed.append(message)

    with client:
        try:
            handle_message()
        except ValueError as e:
            errors.append(str(e))

    assert processed == ["message1"]
    assert len(errors) == 1
    assert errors[0] == "Test error"


def test_sync_batch_consumer_empty_stream() -> None:
    """Test batch consumer behavior with empty message stream."""
    client = MockSyncClient("test-stream", received_messages=[])

    batches = []
    config = SyncConsumerConfig(batch_size=2)

    @client.batch_consumer(config=config)
    def handle_batch(messages: list[str]) -> None:
        batches.append(messages)

    with client:
        handle_batch()

    assert len(batches) == 0


def test_sync_consumer_with_max_messages() -> None:
    """Test consumer with max_messages configuration."""
    client = MockSyncClient("test-stream", received_messages=["message1", "message2", "message3"])

    messages = []
    config = SyncConsumerConfig(max_messages=2)

    @client.consumer(config=config)
    def handle_message(message: str) -> None:
        messages.append(message)

    with client:
        handle_message()

    assert messages == ["message1", "message2"]
