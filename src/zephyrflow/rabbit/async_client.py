"""Asynchronous RabbitMQ messaging client."""

import logging

from collections.abc import AsyncGenerator
from typing import Any, Optional

import aio_pika

from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractQueue
from aio_pika.pool import Pool

from zephyrflow.core.base import AsyncMessagingClient
from zephyrflow.core.factory import register_client

logger = logging.getLogger(__name__)


class AsyncRabbitClient(AsyncMessagingClient[str]):
    """Asynchronous RabbitMQ client implementation."""

    def __init__(
        self,
        stream_name: str,
        queue_name: str,
        rabbitmq_url: str,
        exchange_name: str = "",
        exchange_type: str = "direct",
        exchange_durable: bool = True,
        use_pool: bool = True,
        pool_size: int = 2,
        **kwargs: Any,
    ) -> None:
        """Initialize AsyncRabbitClient.

        Args:
            stream_name: Routing key for messages
            queue_name: Queue name
            rabbitmq_url: RabbitMQ connection URL
            exchange_name: Exchange name
            exchange_type: Exchange type (direct, fanout, topic, headers)
            exchange_durable: Whether exchange survives broker restart
            use_pool: Whether to use connection pooling
            pool_size: Size of the connection pool
        """
        super().__init__(stream_name=stream_name, **kwargs)
        self.queue_name = queue_name
        self.url = rabbitmq_url
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.exchange_durable = exchange_durable
        self.use_pool = use_pool
        self.pool_size = pool_size

        self.connection_pool: Optional[Pool[AbstractConnection]] = None
        self.channel_pool: Optional[Pool[AbstractChannel]] = None
        self.queue: Optional[AbstractQueue] = None

    async def _create_connection(self) -> AbstractConnection:
        """Create a new RabbitMQ connection."""
        try:
            return await aio_pika.connect(self.url)
        except Exception as e:
            logger.error("Failed to create RabbitMQ connection: %s", e)
            raise

    async def _create_channel(self) -> AbstractChannel:
        """Create a new channel from the connection pool."""
        if not self.connection_pool:
            raise RuntimeError("Connection pool not initialized")

        try:
            async with self.connection_pool.acquire() as connection:
                return await connection.channel()
        except Exception as e:
            logger.error("Failed to create RabbitMQ channel: %s", e)
            raise

    async def connect(self) -> None:
        """Establish a connection to RabbitMQ."""
        try:
            if self.use_pool:
                self.connection_pool = Pool(
                    self._create_connection,
                    max_size=self.pool_size,
                )

                self.channel_pool = Pool(
                    self._create_channel,
                    max_size=self.pool_size,
                )

                async with self.channel_pool.acquire() as channel:
                    if self.exchange_name:
                        exchange = await channel.declare_exchange(
                            self.exchange_name,
                            type=self.exchange_type,
                            durable=self.exchange_durable,
                        )
                    else:
                        exchange = channel.default_exchange

                    self.queue = await channel.declare_queue(
                        self.queue_name,
                        durable=True,
                    )
                    await self.queue.bind(exchange, routing_key=self.stream_name)
            else:
                connection = await self._create_connection()
                channel = await connection.channel()

                if self.exchange_name:
                    exchange = await channel.declare_exchange(
                        self.exchange_name,
                        type=self.exchange_type,
                        durable=self.exchange_durable,
                    )
                else:
                    exchange = channel.default_exchange

                self.queue = await channel.declare_queue(
                    self.queue_name,
                    durable=True,
                )
                await self.queue.bind(exchange, routing_key=self.stream_name)
        except Exception as e:
            logger.error("Failed to establish RabbitMQ connection: %s", e)
            await self.close()
            raise

    async def send(self, message: str) -> None:
        """Send a message to the queue."""
        if self.channel_pool is None:
            raise RuntimeError("RabbitMQ connection not established")

        try:
            async with self.channel_pool.acquire() as channel:
                exchange = channel.default_exchange
                if self.exchange_name:
                    exchange = await channel.declare_exchange(
                        self.exchange_name,
                        type=self.exchange_type,
                        durable=self.exchange_durable,
                    )

                await exchange.publish(
                    aio_pika.Message(
                        body=message.encode(),
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    ),
                    routing_key=self.stream_name,
                )
        except Exception as e:
            logger.error("Failed to send message: %s", e)
            raise

    async def receive(self) -> AsyncGenerator[str, None]:  # type: ignore
        """Receive messages from the RabbitMQ queue."""
        if not self.queue:
            raise RuntimeError("RabbitMQ connection not established")

        try:
            async with self.queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        async with message.process():
                            yield message.body.decode()
                    except Exception as e:
                        logger.error("Failed to process message: %s", e)
                        continue
        except Exception as e:
            logger.debug("Queue iterator closed: %s", e)

    async def close(self) -> None:
        """Close the RabbitMQ connection."""
        try:
            if self.channel_pool:
                await self.channel_pool.close()
            if self.connection_pool:
                await self.connection_pool.close()
        except Exception as e:
            logger.error("Error during cleanup: %s", e)


# Register the client
register_client("rabbitmq", "async", AsyncRabbitClient)
