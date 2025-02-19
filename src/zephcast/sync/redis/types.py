"""Type definitions for Redis sync client."""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class RedisConfig:
    """Redis connection configuration."""

    redis_url: str
    max_connections: Optional[int] = None
    min_connections: Optional[int] = None

    def __init__(self, redis_url: str, **kwargs: Any) -> None:
        self.redis_url = redis_url
        self.max_connections = kwargs.pop("max_connections", None)
        self.min_connections = kwargs.pop("min_connections", None)
        for key, value in kwargs.items():
            setattr(self, key, value)
