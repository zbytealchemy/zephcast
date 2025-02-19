"""Synchronous Redis messaging client."""

from collections.abc import Iterator
from typing import Any, Optional

import redis.asyncio

from redis import Redis

from zephcast.core.factory import register_client
from zephcast.core.types import MessageMetadata
from zephcast.sync.base import SyncBaseClient
from zephcast.sync.redis.types import RedisConfig


class RedisClient(SyncBaseClient[str]):
    """Synchronous Redis client implementation."""

    def __init__(
        self,
        stream_name: str,
        config: RedisConfig,
        **kwargs: Any,
    ) -> None:
        """Initialize RedisClient.

        Args:
            stream_name: The name of the Redis stream
            config: Redis configuration
        """
        super().__init__(stream_name=stream_name, **kwargs)
        self.config = config
        self.redis_client: Optional[Redis] = None

    def connect(self) -> None:
        """Establish a connection to Redis."""
        self.redis_client = redis.Redis.from_url(self.config.redis_url)

    def send(self, message: str) -> None:
        """Send a message to the Redis stream."""
        if self.redis_client is None:
            raise RuntimeError("Redis connection not established")
        self.redis_client.xadd(self.stream_name.encode(), {"data": message})

    def receive(self, timeout: float | None = None) -> Iterator[tuple[str, MessageMetadata]]:
        """Receive messages from Redis stream.

        Args:
            timeout: Optional timeout in seconds. None means no timeout.

        Returns:
            Iterator yielding tuples of (message, metadata)
        """
        if not self.redis_client:
            raise RuntimeError("Redis connection not established")

        last_id = "0"
        while True:
            response = self.redis_client.xread(
                {self.stream_name.encode(): last_id.encode()},
                count=1,
                block=1000 if timeout is None else int(timeout * 1000),
            )

            if not response:
                continue

            for _, messages in response:
                for message_id, message_data in messages:
                    message = message_data[b"data"].decode()
                    metadata = MessageMetadata(
                        message_id=message_id.decode(),
                        timestamp=float(message_id.split(b"-")[0].decode()) / 1000,
                    )
                    last_id = message_id.decode()
                    yield message, metadata

    def close(self) -> None:
        """Close the Redis connection."""
        if self.redis_client is not None:
            self.redis_client.close()
            self.redis_client = None


# Register the client
register_client("redis", "sync", RedisClient)
