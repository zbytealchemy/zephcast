"""Synchronous Kafka messaging client."""

import logging

from collections.abc import Iterator
from typing import Any, Generic, Optional, TypeVar

from kafka import KafkaConsumer, KafkaProducer
from kafka.errors import KafkaError

from zephyrflow.core.base import SyncMessagingClient

T = TypeVar("T")
logger = logging.getLogger(__name__)


class SyncKafkaClient(SyncMessagingClient[T], Generic[T]):
    """Synchronous Kafka messaging client."""

    def __init__(
        self,
        stream_name: str,
        bootstrap_servers: str = "localhost:9092",
        group_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize Kafka client.

        Args:
            stream_name: Name of the Kafka topic
            bootstrap_servers: Comma-separated list of Kafka broker addresses
            group_id: Consumer group ID (optional)
            **kwargs: Additional arguments passed to KafkaProducer/KafkaConsumer
        """
        super().__init__(stream_name=stream_name)
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id or f"zephyrflow-{stream_name}"
        self.producer: Optional[KafkaProducer] = None
        self.consumer: Optional[KafkaConsumer] = None
        self.extra_kwargs = kwargs

    def connect(self) -> None:
        """Connect to Kafka."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda x: str(x).encode("utf-8"),
                **self.extra_kwargs,
            )
            self.consumer = KafkaConsumer(
                self.stream_name,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda x: x.decode("utf-8"),
                **self.extra_kwargs,
            )
            logger.info("Connected to Kafka: %s", self.bootstrap_servers)
        except KafkaError as e:
            logger.error("Failed to connect to Kafka: %s", e)
            raise RuntimeError(f"Failed to connect to Kafka: {e}") from e

    def send(self, message: T) -> None:
        """Send a message to Kafka topic.

        Args:
            message: Message to send

        Raises:
            RuntimeError: If client is not connected
        """
        if not self.producer:
            raise RuntimeError("Kafka producer not connected")

        try:
            future = self.producer.send(self.stream_name, message)
            future.get(timeout=10)
            logger.debug("Sent message to Kafka topic %s", self.stream_name)
        except Exception as e:
            logger.error("Failed to send message to Kafka: %s", e)
            raise RuntimeError(f"Failed to send message to Kafka: {e}") from e

    def receive(self) -> Iterator[T]:
        """Receive messages from Kafka topic.

        Yields:
            Received messages

        Raises:
            RuntimeError: If client is not connected
        """
        if not self.consumer:
            raise RuntimeError("Kafka consumer not connected")

        try:
            for message in self.consumer:
                yield message.value
        except Exception as e:
            logger.error("Error receiving messages from Kafka: %s", e)
            raise RuntimeError(f"Error receiving messages from Kafka: {e}") from e

    def close(self) -> None:
        """Close Kafka connections."""
        if self.producer:
            try:
                self.producer.close()
                self.producer = None
            except Exception as e:
                logger.error("Error closing Kafka producer: %s", e)

        if self.consumer:
            try:
                self.consumer.close()
                self.consumer = None
            except Exception as e:
                logger.error("Error closing Kafka consumer: %s", e)
