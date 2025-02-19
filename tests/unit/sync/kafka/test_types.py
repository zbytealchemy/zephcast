"""Unit tests for Kafka configuration types."""
from zephcast.sync.kafka.types import KafkaConfig


def test_kafka_config_defaults() -> None:
    """Test KafkaConfig with default values."""
    config = KafkaConfig(bootstrap_servers="localhost:9092")

    assert config.bootstrap_servers == "localhost:9092"
    assert config.group_id is None
    assert config.client_id is None
    assert config.auto_offset_reset == "latest"
    assert config.enable_auto_commit is True


def test_kafka_config_custom_values() -> None:
    """Test KafkaConfig with custom values."""
    config = KafkaConfig(
        bootstrap_servers="broker1:9092,broker2:9092",
        group_id="test-group",
        client_id="test-client",
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )

    assert config.bootstrap_servers == "broker1:9092,broker2:9092"
    assert config.group_id == "test-group"
    assert config.client_id == "test-client"
    assert config.auto_offset_reset == "earliest"
    assert config.enable_auto_commit is False
