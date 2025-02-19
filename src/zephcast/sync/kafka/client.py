"""Synchronous Kafka client implementation."""

import types

from collections.abc import Iterator
from typing import Any, Optional

from kafka import KafkaConsumer, KafkaProducer

from zephcast.core.types import Message, MessageMetadata
from zephcast.sync.base import SyncBaseClient
from zephcast.sync.kafka.types import KafkaConfig


class KafkaClient(SyncBaseClient):
    """Synchronous Kafka client."""

    def __init__(
        self,
        stream_name: str,
        config: KafkaConfig,
    ) -> None:
        super().__init__(stream_name)
        self.config = config
        self._producer: Optional[KafkaProducer] = None
        self._consumer: Optional[KafkaConsumer] = None

    def connect(self) -> None:
        """Connect to Kafka."""
        if self._connected:
            return

        self._producer = KafkaProducer(
            bootstrap_servers=self.config.bootstrap_servers,
            client_id=self.config.client_id,
        )

        self._consumer = KafkaConsumer(
            self.stream_name,
            bootstrap_servers=self.config.bootstrap_servers,
            group_id=self.config.group_id,
            auto_offset_reset=self.config.auto_offset_reset or "latest",
            enable_auto_commit=self.config.enable_auto_commit or True,
        )

        self._connected = True

    def close(self) -> None:
        """Close Kafka connections."""
        if self._producer:
            self._producer.close()
            self._producer = None
        if self._consumer:
            self._consumer.close()
            self._consumer = None
        self._connected = False

    def send(self, message: Message, **kwargs: Any) -> None:
        """Send a message to Kafka."""
        if not self._connected or not self._producer:
            raise RuntimeError("Client not connected")

        self._producer.send(
            self.stream_name,
            message if isinstance(message, bytes) else str(message).encode(),
            **kwargs,
        )
        self._producer.flush()

    def receive(self, timeout: Optional[float] = None) -> Iterator[tuple[Message, MessageMetadata]]:
        """Receive messages from Kafka."""
        if not self._connected or not self._consumer:
            raise RuntimeError("Client not connected")

        for message in self._consumer:
            metadata = MessageMetadata(
                message_id=f"{message.partition}-{message.offset}",
                timestamp=message.timestamp / 1000.0,
                partition=message.partition,
                offset=message.offset,
            )
            yield message.value.decode(), metadata

    def __enter__(self) -> "KafkaClient":
        """Enter context manager."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[types.TracebackType],
    ) -> None:
        """Exit context manager."""
        self.close()
