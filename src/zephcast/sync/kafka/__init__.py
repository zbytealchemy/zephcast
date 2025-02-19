"""Synchronous Kafka client implementation."""
from zephcast.sync.kafka.client import KafkaClient
from zephcast.sync.kafka.types import KafkaConfig

__all__ = ["KafkaClient", "KafkaConfig"]
