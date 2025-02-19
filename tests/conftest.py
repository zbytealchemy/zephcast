"""Test configuration and fixtures."""
import asyncio
import logging

from collections.abc import AsyncGenerator
from typing import Any

import fakeredis
import pytest
import pytest_asyncio

from zephcast.aio.rabbit import RabbitClient
from zephcast.aio.rabbit.types import RabbitConfig

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def fake_redis() -> fakeredis.FakeRedis:
    """Create a fake Redis server."""
    server = fakeredis.FakeServer()
    redis_client = fakeredis.FakeRedis(server=server)
    return redis_client


@pytest.fixture(scope="session")
def kafka_server(kafka_broker: Any) -> str:
    """Get Kafka server connection string."""
    return f"{kafka_broker[0]}:{kafka_broker[1]}"


@pytest.fixture(scope="session")
def rabbitmq_config(rabbitmq: Any) -> dict[str, str]:
    """Get RabbitMQ configuration."""
    return {"url": f"amqp://{rabbitmq.user}:{rabbitmq.password}@{rabbitmq.host}:{rabbitmq.port}/"}


@pytest_asyncio.fixture
async def rabbit_client(rabbitmq_config: dict[str, str]) -> AsyncGenerator[RabbitClient, None]:
    """Create and cleanup a RabbitMQ client for testing."""
    client = RabbitClient(stream_name="test-stream", config=RabbitConfig(**rabbitmq_config))
    try:
        await client.connect()
        yield client
    finally:
        try:
            await asyncio.wait_for(client.close(), timeout=2)
        except asyncio.TimeoutError:
            logger.warning("Timeout while closing RabbitMQ client in fixture")
        except Exception as e:
            logger.error(f"Error while closing RabbitMQ client in fixture: {e}")
