"""Asynchronous Redis messaging client."""
import asyncio
import logging

from typing import Any, Optional

import redis.asyncio as redis

from zephcast.core.base import AsyncMessagingClient
from zephcast.core.factory import register_client

logger = logging.getLogger(__name__)


class AsyncRedisClient(AsyncMessagingClient[str]):
    """Asynchronous Redis client implementation."""

    def __init__(
        self,
        stream_name: str,
        redis_url: str = "redis://localhost:6379",
        **kwargs: Any,
    ) -> None:
        """Initialize AsyncRedisClient.

        Args:
            stream_name: The name of the Redis stream
            redis_url: The URL of the Redis server
        """
        super().__init__(stream_name=stream_name, **kwargs)
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Establish a connection to Redis."""
        try:
            self.redis_client = redis.Redis.from_url(self.redis_url)
        except Exception as e:
            logger.error("Failed to connect to Redis: %s", e)
            raise

    async def send(self, message: str) -> None:
        """Send a message to the Redis stream.

        Args:
            message: The message to send
        """
        if self.redis_client is None:
            raise RuntimeError("Redis connection not established")
        try:
            await self.redis_client.xadd(self.stream_name, {"data": message})
        except Exception as e:
            logger.error("Failed to send message: %s", e)
            raise

    async def receive(self) -> Any:
        """Receive messages from the Redis stream."""
        if not self.redis_client:
            raise RuntimeError("Redis connection not established")

        last_id = "0"
        while True:
            try:
                entries = await self.redis_client.xread(
                    {self.stream_name: last_id},
                    count=1,
                )

                if entries:
                    for _, messages in entries:
                        for message_id, data in messages:
                            last_id = message_id
                            yield data[b"data"].decode()
                else:
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error("Error receiving message: %s", e)
                await asyncio.sleep(0.1)

    async def close(self) -> None:
        """Close the Redis client."""
        if self.redis_client:
            await self.redis_client.aclose()  # type: ignore
            self.redis_client = None


# Register the client
register_client("redis", "async", AsyncRedisClient)
