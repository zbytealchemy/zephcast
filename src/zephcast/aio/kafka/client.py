"""Asynchronous Kafka client implementation."""
import asyncio
import json
import logging

from collections.abc import AsyncGenerator
from typing import Any, Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError
from typing_extensions import override

from zephcast.aio.base import AsyncBaseClient
from zephcast.aio.kafka.types import KafkaConfig
from zephcast.aio.retry import AsyncRetryConfig, retry
from zephcast.core.exceptions import ConnectionError as ZephConnectionError
from zephcast.core.types import Message, MessageMetadata

logger = logging.getLogger(__name__)


class KafkaClient(AsyncBaseClient[Message]):
    """Asynchronous Kafka client."""

    def __init__(
        self,
        stream_name: str,
        connection_config: KafkaConfig,
    ) -> None:
        super().__init__(stream_name)
        self.connection_config = connection_config
        self._producer: Optional[AIOKafkaProducer] = None
        self._consumer: Optional[AIOKafkaConsumer] = None

    @override
    @retry(
        AsyncRetryConfig(
            max_retries=1,
            retry_sleep=0.1,
            backoff_factor=1.0,
            exceptions=(KafkaConnectionError, ConnectionError),
        )
    )
    async def connect(self) -> None:
        """Connect to Kafka."""
        if self._connected:
            return

        logger.debug("Connecting to Kafka...")
        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.connection_config.bootstrap_servers,
                client_id=getattr(self.connection_config, "client_id", None),
            )

            self._consumer = AIOKafkaConsumer(
                self.stream_name,
                bootstrap_servers=self.connection_config.bootstrap_servers,
                group_id=getattr(self.connection_config, "group_id", None),
                auto_offset_reset=getattr(self.connection_config, "auto_offset_reset", "latest"),
                enable_auto_commit=getattr(self.connection_config, "enable_auto_commit", True),
            )

            await self._producer.start()
            await self._consumer.start()
            self._connected = True
            logger.info("Successfully connected to Kafka")
        except Exception as e:
            self._producer = None
            self._consumer = None
            self._connected = False
            raise ZephConnectionError("Failed to connect to KafkaClient") from e

    async def close(self) -> None:
        """Close Kafka connections."""
        logger.debug("Closing %s connection...", self.__class__.__name__)

        if not self._connected:
            self._producer = None
            self._consumer = None
            self._connected = False
            return

        timeout = 0.5

        if self._producer:
            try:
                await asyncio.shield(asyncio.wait_for(self._producer.stop(), timeout=timeout))
            except (Exception, asyncio.TimeoutError) as e:
                logger.warning("Failed to stop producer: %s", e)
            self._producer = None

        if self._consumer:
            try:
                await asyncio.shield(asyncio.wait_for(self._consumer.stop(), timeout=timeout))
            except (Exception, asyncio.TimeoutError) as e:
                logger.warning("Failed to stop consumer: %s", e)
            self._consumer = None

        self._connected = False

    async def send(self, message: Message, **kwargs: Any) -> None:
        """Send a message to Kafka."""
        if not self._connected or not self._producer:
            raise RuntimeError("Client not connected")

        if isinstance(message, str):
            encoded = message.encode()
        elif isinstance(message, bytes):
            encoded = message
        elif isinstance(message, dict):
            encoded = json.dumps(message).encode()
        else:
            raise TypeError(f"Unsupported message type: {type(message)}")

        await self._producer.send_and_wait(self.stream_name, encoded, **kwargs)

    async def receive(  # type: ignore[override]
        self, timeout: Optional[float] = None
    ) -> AsyncGenerator[tuple[Message, MessageMetadata], None]:
        """Receive messages from Kafka.

        Args:
            timeout: Optional timeout in seconds. None means no timeout.

        Returns:
            AsyncGenerator yielding tuples of (message, metadata)
        """
        if not self._connected or not self._consumer:
            raise RuntimeError("Client not connected")

        async for message in self._consumer:
            metadata = MessageMetadata(
                message_id=f"{message.partition}-{message.offset}",
                timestamp=message.timestamp / 1000.0,
                partition=message.partition,
                offset=message.offset,
            )
            yield message.value.decode(), metadata
