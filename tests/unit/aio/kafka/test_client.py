"""Unit tests for async Kafka client."""
from unittest.mock import AsyncMock, patch

import pytest

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from zephcast.aio.kafka.client import KafkaClient
from zephcast.aio.kafka.types import KafkaConfig
from zephcast.core.exceptions import ConnectionError


@pytest.fixture
def kafka_config() -> KafkaConfig:
    """Create a Kafka configuration for testing."""
    return KafkaConfig(
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        client_id="test-client",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )


@pytest.fixture
def kafka_client(kafka_config: KafkaConfig) -> KafkaClient:
    """Create a Kafka client for testing."""
    return KafkaClient(stream_name="test-topic", connection_config=kafka_config)


@pytest.mark.asyncio
@patch("zephcast.aio.kafka.client.AIOKafkaProducer")
@patch("zephcast.aio.kafka.client.AIOKafkaConsumer")
async def test_kafka_client_connect(
    mock_consumer: AsyncMock, mock_producer: AsyncMock, kafka_client: KafkaClient
) -> None:
    """Test Kafka client connection."""
    producer_instance = AsyncMock(spec=AIOKafkaProducer)
    consumer_instance = AsyncMock(spec=AIOKafkaConsumer)

    mock_producer.return_value = producer_instance
    mock_consumer.return_value = consumer_instance

    await kafka_client.connect()
    assert kafka_client._connected

    producer_instance.start.assert_called_once()
    consumer_instance.start.assert_called_once()


@pytest.mark.asyncio
@patch("zephcast.aio.kafka.client.AIOKafkaProducer")
@patch("zephcast.aio.kafka.client.AIOKafkaConsumer")
async def test_kafka_client_close(
    mock_consumer: AsyncMock, mock_producer: AsyncMock, kafka_client: KafkaClient
) -> None:
    """Test Kafka client close."""
    producer_instance = AsyncMock(spec=AIOKafkaProducer)
    consumer_instance = AsyncMock(spec=AIOKafkaConsumer)

    mock_producer.return_value = producer_instance
    mock_consumer.return_value = consumer_instance

    await kafka_client.connect()
    await kafka_client.close()

    assert not kafka_client._connected
    producer_instance.stop.assert_called_once()
    consumer_instance.stop.assert_called_once()


@pytest.mark.asyncio
@patch("zephcast.aio.kafka.client.AIOKafkaProducer")
@patch("zephcast.aio.kafka.client.AIOKafkaConsumer")
async def test_kafka_client_connection_error(mock_consumer: AsyncMock, mock_producer: AsyncMock) -> None:
    """Test async Kafka client connection error."""
    producer_instance = AsyncMock(spec=AIOKafkaProducer)
    producer_instance.start.side_effect = Exception("Failed to connect")
    mock_producer.return_value = producer_instance

    consumer_instance = AsyncMock(spec=AIOKafkaConsumer)
    mock_consumer.return_value = consumer_instance

    config = KafkaConfig(bootstrap_servers="invalid:9092", group_id="test-group", client_id="test-client")
    client = KafkaClient(stream_name="test-topic", connection_config=config)

    with pytest.raises(ConnectionError) as exc_info:
        await client.connect()

    assert "Failed to connect to KafkaClient" in str(exc_info.value)
    assert not client._connected

    if producer_instance.stop.called:
        producer_instance.stop.assert_called_once()
    if consumer_instance.stop.called:
        consumer_instance.stop.assert_called_once()
