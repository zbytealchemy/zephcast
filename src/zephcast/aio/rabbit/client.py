"""Asynchronous RabbitMQ client implementation."""

import asyncio
import logging

from collections.abc import AsyncGenerator
from typing import Any, Optional

import aio_pika

from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue
from aio_pika.exceptions import AMQPConnectionError
from aio_pika.pool import Pool
from typing_extensions import override

from zephcast.aio.base import AsyncBaseClient
from zephcast.aio.rabbit.types import RabbitConfig
from zephcast.aio.retry import AsyncRetryConfig, retry
from zephcast.core.exceptions import ConnectionError as ZephConnectionError
from zephcast.core.factory import register_client
from zephcast.core.types import Message, MessageMetadata
from zephcast.core.utils import serialize_message

logger = logging.getLogger(__name__)


class RabbitClient(AsyncBaseClient):
    """Asynchronous RabbitMQ client.

    Provides high-level interface for working with RabbitMQ message broker.
    Supports both publishing and consuming messages with automatic connection
    management and error handling.

    Args:
        stream_name: The routing key to use for message routing
        config: RabbitMQ configuration options
    """

    def __init__(self, stream_name: str, config: RabbitConfig) -> None:
        """Initialize RabbitMQ client.

        Args:
            stream_name: The routing key to use for message routing
            config: RabbitMQ configuration options
        """
        self.stream_name = stream_name
        self.config = config
        self._connected = False
        self._connection: Optional[AbstractConnection] = None
        self._channel: Optional[AbstractChannel] = None
        self._connection_pool: Optional[Pool] = None
        self._channel_pool: Optional[Pool] = None
        self._queue: Optional[AbstractQueue] = None

    @override
    @retry(
        AsyncRetryConfig(
            max_retries=1,
            retry_sleep=0.1,
            backoff_factor=1.0,
            exceptions=(AMQPConnectionError, ConnectionError),
            on_retry=lambda attempt, exc: logger.warning("Connection attempt %d failed: %s", attempt, exc),
        )
    )
    async def connect(self) -> None:
        """Connect to RabbitMQ server."""
        if self._connected:
            return

        logger.debug("Connecting to RabbitMQ...")
        try:
            self._connection = await self._create_connection()
            await asyncio.shield(self._connection.connect())

            self._channel = await asyncio.shield(self._connection.channel())
            await asyncio.shield(self._setup_exchange_and_queue(self._channel))

            if self.config.use_pool:
                self._connection_pool = Pool(self._create_connection, max_size=self.config.pool_size)
                self._channel_pool = Pool(self._create_channel, max_size=self.config.pool_size)

            self._connected = True
            logger.info("Successfully connected to RabbitMQ")
        except Exception as e:
            self._connection = None
            self._channel = None
            self._connection_pool = None
            self._channel_pool = None
            self._queue = None
            self._connected = False
            raise ZephConnectionError("Failed to connect to RabbitClient") from e

    async def _do_connect(self) -> None:
        """Internal method to handle connection setup."""
        self._connection = await self._create_connection()
        await self._connection.connect()

        if self.config.use_pool:
            self._connection_pool = Pool(self._create_connection, max_size=self.config.pool_size)
            self._channel_pool = Pool(self._create_channel, max_size=self.config.pool_size)

        self._channel = await self._connection.channel()
        await self._setup_exchange_and_queue(self._channel)

    async def _create_connection(self) -> AbstractConnection:
        """Create a new RabbitMQ connection."""
        try:
            connection = await aio_pika.connect_robust(
                self.config.url,
                client_properties={"connection_name": f"zephcast_{self.stream_name}"},
            )
            return connection
        except AMQPConnectionError:
            raise
        except Exception as e:
            raise ConnectionError(f"Failed to create connection: {e!s}") from e

    async def _create_channel(self) -> AbstractChannel:
        """Create a new RabbitMQ channel."""
        if self.config.use_pool:
            if not self._connection_pool:
                raise RuntimeError("Connection pool not initialized")
            async with self._connection_pool.acquire() as connection:
                if not isinstance(connection, AbstractConnection):
                    raise TypeError("Expected AbstractConnection from connection pool")
                channel = await connection.channel()
                if not isinstance(channel, AbstractChannel):
                    raise TypeError("Expected AbstractChannel from connection")
                return channel
        else:
            if not self._connection:
                raise RuntimeError("Connection not established")
            return await self._connection.channel()

    async def _setup_exchange_and_queue(self, channel: AbstractChannel) -> None:
        """Set up exchange and queue."""
        exchange_name = getattr(self.config, "exchange_name", "")
        exchange = channel.default_exchange

        if exchange_name:
            exchange = await channel.declare_exchange(
                exchange_name,
                type=getattr(self.config, "exchange_type", "direct"),
                durable=getattr(self.config, "exchange_durable", True),
            )

        self._queue = await channel.declare_queue(
            self.config.queue_name,
            durable=getattr(self.config, "queue_durable", True),
            auto_delete=False,
        )

        await self._queue.bind(
            exchange=exchange,
            routing_key=self.stream_name,
        )

    async def send(self, message: Message, **kwargs: Any) -> None:
        """Send a message to RabbitMQ."""
        if not self._connected:
            raise RuntimeError("Client not connected")

        if self.config.use_pool and self._channel_pool:
            async with self._channel_pool.acquire() as channel:
                await self._do_send(channel, message, **kwargs)
        else:
            if not self._channel:
                raise RuntimeError("Channel not available")
            await self._do_send(self._channel, message, **kwargs)

    async def _do_send(self, channel: AbstractChannel, message: str | bytes | dict, **kwargs: Any) -> None:
        """Internal method to send a message using the provided channel.

        Args:
            channel: The RabbitMQ channel to use
            message: The message to send
            **kwargs: Additional message properties
        """
        if self.config.exchange_name:
            exchange = await channel.get_exchange(self.config.exchange_name)
        else:
            exchange = channel.default_exchange

        message_body = serialize_message(message)

        await exchange.publish(
            aio_pika.Message(body=message_body, delivery_mode=aio_pika.DeliveryMode.PERSISTENT, **kwargs),
            routing_key=self.stream_name,
        )

    @property
    def is_connected(self) -> bool:
        """Check if client is connected to RabbitMQ."""
        return self._connected

    @override
    async def receive(  # type: ignore[override]
        self, timeout: float | None = None
    ) -> AsyncGenerator[tuple[str | bytes | dict[str, Any], MessageMetadata], None]:
        """Receive messages from RabbitMQ queue.

        Args:
            timeout: Optional timeout in seconds. None means no timeout.

        Returns:
            AsyncGenerator yielding tuples of (message, metadata)
        """
        if not self._connected:
            raise RuntimeError("Client not connected")

        if not self._queue:
            raise RuntimeError("Queue not initialized")

        async for message in self._queue.iterator():
            try:
                async with message.process():
                    body = message.body.decode()
                    msg_timestamp = message.timestamp
                    timestamp = 0.0

                    timestamp = 0.0
                    if msg_timestamp is not None:
                        if hasattr(msg_timestamp, "timestamp"):
                            timestamp = msg_timestamp.timestamp()
                        else:
                            try:
                                timestamp = float(str(msg_timestamp))
                            except (TypeError, ValueError):
                                pass

                    metadata = MessageMetadata(
                        message_id=str(message.message_id)
                        if message.message_id
                        else str(message.delivery_tag),
                        timestamp=timestamp,
                        delivery_tag=message.delivery_tag,
                    )

                    yield body, metadata
            except Exception as e:
                logger.error("Error processing message: %s", e)
                continue

    async def close(self) -> None:
        """Close the RabbitMQ connection."""
        # For error cases (like invalid connection), just clean up references
        if not self._connected:
            self._channel_pool = None
            self._connection_pool = None
            self._connection = None
            self._queue = None
            self._connected = False
            return

        # For normal cases, try to clean up properly with timeouts
        timeout = 0.5  # Reduced timeout for faster failure

        if self._channel_pool:
            try:
                await asyncio.shield(asyncio.wait_for(self._channel_pool.close(), timeout=timeout))
            except (Exception, asyncio.TimeoutError) as e:
                logger.warning("Failed to close channel pool: %s", e)
            self._channel_pool = None

        if self._connection_pool:
            try:
                await asyncio.shield(asyncio.wait_for(self._connection_pool.close(), timeout=timeout))
            except (Exception, asyncio.TimeoutError) as e:
                logger.warning("Failed to close connection pool: %s", e)
            self._connection_pool = None

        if self._connection:
            try:
                await asyncio.shield(asyncio.wait_for(self._connection.close(), timeout=timeout))
            except (Exception, asyncio.TimeoutError) as e:
                logger.warning("Failed to close connection: %s", e)
            self._connection = None

        self._queue = None
        self._connected = False


# Register the client
register_client("rabbitmq", "async", RabbitClient)
