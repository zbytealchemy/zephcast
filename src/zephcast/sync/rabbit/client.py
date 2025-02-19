"""Synchronous RabbitMQ client implementation."""
import logging

from collections.abc import Iterator
from types import TracebackType
from typing import TYPE_CHECKING, Any, Optional

import pika

from zephcast.core.exceptions import ConnectionError
from zephcast.core.factory import register_client
from zephcast.core.types import Message, MessageMetadata
from zephcast.sync.base import SyncBaseClient
from zephcast.sync.rabbit.types import RabbitConfig

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel


class RabbitClient(SyncBaseClient):
    """Synchronous RabbitMQ client."""

    def __init__(
        self,
        stream_name: str,
        config: RabbitConfig,
    ) -> None:
        super().__init__(stream_name)
        self.config = config
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional["BlockingChannel"] = None
        self._queue_name = self.config.queue_name or str(self.stream_name)

    def connect(self) -> None:
        """Connect to RabbitMQ."""
        if self._connected:
            return

        logger.debug("Connecting to RabbitMQ...")
        try:
            parameters = pika.URLParameters(self.config.url)
            self._connection = pika.BlockingConnection(parameters)
            self._channel = self._connection.channel()

            exchange_name = self.config.exchange_name or ""
            if exchange_name:
                self._channel.exchange_declare(
                    exchange=exchange_name,
                    exchange_type=self.config.exchange_type or "direct",
                    durable=self.config.exchange_durable or True,
                )

            # Declare queue and bind it
            self._channel.queue_declare(self._queue_name, durable=True)
            self._channel.queue_bind(
                queue=self._queue_name,
                exchange=exchange_name,
                routing_key=self.stream_name,
            )
            self._connected = True
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            self._connected = False
            logger.error("%s: Connection error occurred - %s", self.__class__.__name__, str(e))
            raise ConnectionError(f"Failed to connect to {self.__class__.__name__}: {e!s}") from e

        self._connected = True

    def close(self) -> None:
        """Close RabbitMQ connection."""
        logger.debug("Closing %s connection...", self.__class__.__name__)
        if self._channel:
            self._channel.close()
            self._channel = None
        if self._connection:
            self._connection.close()
            self._connection = None
        self._connected = False
        logger.debug("%s connection closed", self.__class__.__name__)

    def send(self, message: Message, **kwargs: Any) -> None:
        """Send a message to RabbitMQ."""
        if not self._connected or not self._channel:
            raise RuntimeError("Client not connected")

        exchange = self.config.exchange_name or ""
        self._channel.basic_publish(
            exchange=exchange,
            routing_key=self.stream_name,
            body=message if isinstance(message, bytes) else str(message).encode(),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
                **kwargs,
            ),
        )

    def receive(self, timeout: Optional[float] = None) -> Iterator[tuple[Message, MessageMetadata]]:
        """Receive messages from RabbitMQ."""
        if not self._connected or not self._channel:
            raise RuntimeError("Client not connected")

        while True:
            method_frame, properties, body = self._channel.basic_get(
                queue=self._queue_name,
                auto_ack=True,
            )

            if method_frame:
                metadata = MessageMetadata(
                    message_id=properties.message_id or str(method_frame.delivery_tag),
                    timestamp=properties.timestamp or 0.0,
                    delivery_tag=method_frame.delivery_tag,
                )
                yield body.decode(), metadata

    def __enter__(self) -> "RabbitClient":
        """Enter context manager."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Exit context manager."""
        self.close()


# Register the client
register_client("rabbit", "sync", RabbitClient)
