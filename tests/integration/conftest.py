"""Pytest configuration for integration tests."""

import asyncio
import os
import uuid

from collections.abc import AsyncGenerator, Generator

import pytest

from kafka import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError

from msgflow.kafka.async_client import AsyncKafkaClient
from msgflow.kafka.sync_client import SyncKafkaClient
from msgflow.rabbit.async_client import AsyncRabbitClient
from msgflow.redis.async_client import AsyncRedisClient
from msgflow.redis.sync_client import SyncRedisClient

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TEST_TIMEOUT = 30


@pytest.fixture(scope="session")
def kafka_admin() -> Generator[KafkaAdminClient, None, None]:
    """Create a Kafka admin client for managing topics."""
    try:
        admin = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
        yield admin
    except Exception as e:
        pytest.skip(f"Kafka not available: {e}")
    finally:
        try:
            admin.close()
        except Exception as e:
            print(f"Warning: Failed to close Kafka admin client: {e}")


@pytest.fixture
def kafka_topic(kafka_admin: KafkaAdminClient) -> Generator[str, None, None]:
    """Create a unique Kafka topic for testing."""
    topic_name = f"test-topic-{uuid.uuid4()}"
    try:
        kafka_admin.create_topics(
            [NewTopic(name=topic_name, num_partitions=1, replication_factor=1)]
        )
    except TopicAlreadyExistsError:
        pass
    except KafkaError as e:
        pytest.fail(f"Failed to create Kafka topic: {e}")

    yield topic_name

    try:
        kafka_admin.delete_topics([topic_name])
    except Exception as e:
        print(f"Warning: Failed to delete Kafka topic {topic_name}: {e}")


@pytest.fixture
def redis_stream() -> Generator[str, None, None]:
    """Create a unique Redis stream name for testing."""
    stream_name = f"test-stream-{uuid.uuid4()}"
    yield stream_name


@pytest.fixture
def rabbitmq_queue() -> Generator[str, None, None]:
    """Create a unique RabbitMQ queue name for testing."""
    queue_name = f"test-queue-{uuid.uuid4()}"
    yield queue_name


@pytest.fixture
def kafka_async_client(kafka_topic: str) -> AsyncKafkaClient:
    """Create an async Kafka client for testing."""
    client = AsyncKafkaClient(
        stream_name=kafka_topic,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
    )
    return client


@pytest.fixture
def kafka_sync_client(kafka_topic: str) -> Generator[SyncKafkaClient, None, None]:
    """Create a sync Kafka client for testing."""
    client: SyncKafkaClient = SyncKafkaClient(
        stream_name=kafka_topic, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )

    try:
        client.connect()
        yield client
    except Exception as e:
        pytest.fail(f"Failed to create Kafka client: {e}")
    finally:
        try:
            client.close()
        except Exception as e:
            print(f"Warning: Failed to close Kafka client: {e}")


@pytest.fixture
async def rabbitmq_async_client(rabbitmq_queue: str) -> AsyncGenerator[AsyncRabbitClient, None]:
    """Create an async RabbitMQ client for testing."""
    client = AsyncRabbitClient(
        stream_name="test-routing-key", queue_name=rabbitmq_queue, rabbitmq_url=RABBITMQ_URL
    )
    try:
        await asyncio.wait_for(client.connect(), timeout=TEST_TIMEOUT)
        async with client:
            yield client
    except asyncio.TimeoutError:
        pytest.fail("Timeout while connecting to RabbitMQ")
    except Exception as e:
        pytest.fail(f"Failed to create RabbitMQ client: {e}")


@pytest.fixture
async def redis_async_client(redis_stream: str) -> AsyncGenerator[AsyncRedisClient, None]:
    """Create an async Redis client for testing."""
    client = AsyncRedisClient(stream_name=redis_stream, redis_url=REDIS_URL)
    try:
        await asyncio.wait_for(client.connect(), timeout=TEST_TIMEOUT)
        async with client:
            yield client
    except asyncio.TimeoutError:
        pytest.fail("Timeout while connecting to Redis")
    except Exception as e:
        pytest.fail(f"Failed to create Redis client: {e}")


@pytest.fixture
def redis_sync_client(redis_stream: str) -> Generator[SyncRedisClient, None, None]:
    """Create a sync Redis client for testing."""
    client = SyncRedisClient(stream_name=redis_stream, redis_url=REDIS_URL)
    try:
        client.connect()
        yield client
    except Exception as e:
        pytest.fail(f"Failed to create Redis client: {e}")
    finally:
        try:
            client.close()
        except Exception as e:
            print(f"Warning: Failed to close Redis client: {e}")
