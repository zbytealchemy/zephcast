"""Type definitions for Redis async client."""
from dataclasses import dataclass
from typing import Any, Optional

from zephcast.core.exceptions import ConfigurationError


@dataclass
class RedisConfig:
    """Redis connection configuration.

    Args:
        redis_url: Redis connection URL (e.g., 'redis://localhost:6379/0')
        max_connections: Maximum number of connections in the pool
        min_connections: Minimum number of connections in the pool

    Raises:
        ConfigurationError: If any configuration values are invalid
    """

    redis_url: str
    max_connections: Optional[int] = None
    min_connections: Optional[int] = None

    def __init__(self, redis_url: str, **kwargs: Any) -> None:
        if not redis_url or not isinstance(redis_url, str):
            raise ConfigurationError("redis_url must be a non-empty string")

        self.redis_url = redis_url

        # Validate max_connections
        self.max_connections = kwargs.pop("max_connections", None)
        if self.max_connections is not None:
            if not isinstance(self.max_connections, int) or self.max_connections < 1:
                raise ConfigurationError("max_connections must be a positive integer")

        # Validate min_connections
        self.min_connections = kwargs.pop("min_connections", None)
        if self.min_connections is not None:
            if not isinstance(self.min_connections, int) or self.min_connections < 0:
                raise ConfigurationError("min_connections must be a non-negative integer")

            # Validate min_connections is less than or equal to max_connections
            if self.max_connections is not None and self.min_connections > self.max_connections:
                raise ConfigurationError("min_connections cannot be greater than max_connections")

        # Allow additional attributes to be set
        for key, value in kwargs.items():
            setattr(self, key, value)
