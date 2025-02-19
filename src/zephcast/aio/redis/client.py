"""Asynchronous Redis messaging client."""
import json
import logging

from collections.abc import AsyncGenerator
from typing import Any, Optional

import redis.asyncio as redis

from typing_extensions import override

from zephcast.aio.base import AsyncBaseClient
from zephcast.aio.redis.types import RedisConfig
from zephcast.aio.retry import AsyncRetryConfig, retry
from zephcast.core.factory import register_client
from zephcast.core.types import Message, MessageMetadata

logger = logging.getLogger(__name__)


class RedisClient(AsyncBaseClient[Message]):
    """Asynchronous Redis client implementation."""

    def __init__(
        self,
        stream_name: str,
        config: RedisConfig,
        **kwargs: Any,
    ) -> None:
        """Initialize RedisClient."""
        super().__init__(stream_name)
        self.config = config
        self._client: redis.Redis | None = None
        self._connected = False

    @override
    @retry(
        AsyncRetryConfig(max_retries=3, retry_sleep=1.0, backoff_factor=2.0, exceptions=(ConnectionError,))
    )
    async def connect(self) -> None:
        """Connect to Redis."""
        if self._connected:
            return

        logger.debug("Connecting to Redis...")
        self._client = await redis.Redis.from_url(self.config.redis_url)
        if self._client:
            await self._client.ping()
        self._connected = True
        logger.info("Successfully connected to Redis")

    async def send(self, message: Message, **kwargs: Any) -> None:
        """Send a message to the Redis stream."""
        if not self._connected or self._client is None:
            raise RuntimeError("Redis connection not established")

        # Convert message to string format that Redis accepts
        if isinstance(message, bytes):
            data = message.decode()
        elif isinstance(message, dict):
            data = json.dumps(message)
        else:
            data = str(message)

        try:
            await self._client.xadd(self.stream_name, {"data": data})
        except Exception as e:
            logger.error("Failed to send message: %s", e)
            raise

    @override
    async def receive(  # type: ignore[override]
        self, timeout: Optional[float] = None
    ) -> AsyncGenerator[tuple[str | bytes | dict[str, Any], MessageMetadata], None]:
        """Receive messages from Redis stream.

        Args:
            timeout: Optional timeout in seconds. None means no timeout.

        Returns:
            AsyncGenerator yielding tuples of (message, metadata)
        """
        if not self._connected or not self._client:
            raise RuntimeError("Redis connection not established")

        last_id = "0"
        while True:
            try:
                response = await self._client.xread(
                    {self.stream_name: last_id},
                    count=1,
                    block=int(timeout * 1000) if timeout else None,
                )

                if not response:
                    continue

                for _, messages in response:
                    for message_id, fields in messages:
                        message_id_str = message_id.decode()
                        last_id = message_id_str

                        timestamp = float(message_id_str.split("-")[0]) / 1000
                        metadata = MessageMetadata(message_id=message_id_str, timestamp=timestamp)

                        data = fields[b"data"]
                        if isinstance(data, bytes):
                            data = data.decode()

                        yield data, metadata

            except Exception as e:
                logger.error("Error receiving message: %s", e)
                raise

    async def close(self) -> None:
        """Close the Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None
        self._connected = False


# Register the client
register_client("redis", "async", RedisClient)
