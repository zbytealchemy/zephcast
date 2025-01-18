"""Synchronous Redis messaging client."""

from collections.abc import Iterator
from typing import Any, Optional, cast

import redis

from zephcast.core.base import SyncMessagingClient
from zephcast.core.factory import register_client


class SyncRedisClient(SyncMessagingClient[str]):
    """Synchronous Redis client implementation."""

    def __init__(
        self,
        stream_name: str,
        redis_url: str = "redis://localhost:6379",
        **kwargs: Any,
    ) -> None:
        """Initialize RedisClient.

        Args:
            stream_name: The name of the Redis stream
            redis_url: The URL of the Redis server
        """
        super().__init__(stream_name=stream_name, **kwargs)
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None

    def connect(self) -> None:
        """Establish a connection to Redis."""
        self.redis_client = redis.Redis.from_url(self.redis_url)

    def send(self, message: str) -> None:
        """Send a message to the Redis stream."""
        if self.redis_client is None:
            raise RuntimeError("Redis connection not established")
        self.redis_client.xadd(self.stream_name, {"data": message})

    def receive(self) -> Iterator[str]:
        """Receive messages from the Redis stream."""
        if self.redis_client is None:
            raise RuntimeError("Redis connection not established")

        last_id = b"0"
        while True:
            entries = cast(
                list[tuple[bytes, list[tuple[bytes, dict[bytes, bytes]]]]],
                self.redis_client.xread(
                    {self.stream_name: last_id},
                    count=1,
                    block=1000,
                ),
            )

            if entries:
                for _, messages in entries:
                    for message_id, data in messages:
                        last_id = message_id
                        yield data[b"data"].decode()
            else:
                import time

                time.sleep(0.1)

    def close(self) -> None:
        """Close the Redis connection."""
        if self.redis_client is not None:
            self.redis_client.close()
            self.redis_client = None


# Register the client
register_client("redis", "sync", SyncRedisClient)
