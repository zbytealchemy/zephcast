"""Asynchronous Kafka messaging client."""

import logging

from collections.abc import AsyncGenerator
from typing import Any, Optional, cast

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from msgflow.core.base import AsyncMessagingClient

logger = logging.getLogger(__name__)


class AsyncKafkaClient(AsyncMessagingClient[str]):
    """Asynchronous Kafka messaging client."""

    def __init__(
        self,
        stream_name: str,
        bootstrap_servers: str = "localhost:9092",
        group_id: Optional[str] = None,
        auto_offset_reset: str = "latest",
        enable_auto_commit: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize async Kafka client.

        Args:
            stream_name: Name of the Kafka topic
            bootstrap_servers: Comma-separated list of Kafka broker addresses
            group_id: Consumer group ID (optional)
            auto_offset_reset: Where to start consuming from ('latest' or 'earliest')
            enable_auto_commit: Whether to automatically commit offsets
            **kwargs: Additional arguments passed to AIOKafkaProducer/AIOKafkaConsumer
        """
        super().__init__(stream_name=stream_name)
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id or f"msgflow-async-{stream_name}"
        self.auto_offset_reset = auto_offset_reset
        self.enable_auto_commit = enable_auto_commit
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        self.extra_kwargs = kwargs

    async def connect(self) -> None:
        """Connect to Kafka."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                **self.extra_kwargs,
            )
            await self.producer.start()

            self.consumer = AIOKafkaConsumer(
                self.stream_name,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=self.enable_auto_commit,
                **self.extra_kwargs,
            )
            await self.consumer.start()
        except Exception as e:
            logger.error("Failed to connect to Kafka: %s", e)
            await self.close()
            raise

    async def send(self, message: str) -> None:
        """Send a message to Kafka topic."""
        if not self.producer:
            raise RuntimeError("Kafka producer not connected")

        try:
            await self.producer.send_and_wait(
                self.stream_name,
                message.encode(),
            )
        except Exception as e:
            logger.error("Failed to send message to Kafka: %s", e)
            raise

    async def receive(self) -> AsyncGenerator[str, None]:  # type: ignore
        """Receive messages from Kafka topic."""
        if not self.consumer:
            raise RuntimeError("Kafka consumer not connected")

        try:
            async for message in self.consumer:
                yield cast(str, message.value.decode())
        except Exception as e:
            logger.error("Error receiving message from Kafka: %s", e)
            raise

    async def close(self) -> None:
        """Close Kafka connections."""
        try:
            if self.consumer:
                await self.consumer.stop()
            if self.producer:
                await self.producer.stop()
        except Exception as e:
            logger.error("Error closing Kafka connections: %s", e)
        finally:
            self.consumer = None
            self.producer = None

    async def __aenter__(self) -> "AsyncKafkaClient":
        """Enter async context manager."""
        if not self.producer or not self.consumer:
            await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit async context manager."""
        await self.close()

    def __aiter__(self) -> "AsyncKafkaClient":
        """Return async iterator."""
        return self

    async def __anext__(self) -> str:
        """Get next message."""
        async for message in self.receive():
            return message
        raise StopAsyncIteration
