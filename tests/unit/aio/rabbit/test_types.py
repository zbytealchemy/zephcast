"""Unit tests for RabbitMQ types."""

from zephcast.aio.rabbit.types import RabbitConfig


def test_rabbit_config_defaults() -> None:
    """Test RabbitConfig with default values."""
    config = RabbitConfig(
        url="amqp://localhost:5672",
        queue_name="test-queue",
        routing_key="test-key",
        exchange_type="direct",
        exchange_durable=True,
        queue_durable=True,
    )
    assert config.url == "amqp://localhost:5672"
    assert config.queue_name == "test-queue"
    assert config.routing_key == "test-key"
    assert config.exchange_name is None
    assert config.exchange_type == "direct"
    assert config.exchange_durable is True
    assert config.queue_durable is True


def test_rabbit_config_custom_values() -> None:
    """Test RabbitConfig with custom values."""
    config = RabbitConfig(
        url="amqp://localhost:5672",
        queue_name="test-queue",
        routing_key="test-key",
        exchange_name="test-exchange",
        exchange_type="fanout",
        exchange_durable=False,
        queue_durable=False,
    )
    assert config.url == "amqp://localhost:5672"
    assert config.queue_name == "test-queue"
    assert config.routing_key == "test-key"
    assert config.exchange_name == "test-exchange"
    assert config.exchange_type == "fanout"
    assert config.exchange_durable is False
    assert config.queue_durable is False
