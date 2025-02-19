"""Type definitions for RabbitMQ async client."""
from dataclasses import dataclass
from typing import Any, Literal, Optional

from zephcast.core.exceptions import ConfigurationError


@dataclass
class RabbitConfig:
    """RabbitMQ connection configuration.

    Args:
        url: RabbitMQ connection URL (e.g., 'amqp://localhost:5672')
        queue_name: Name of the queue to use. If not provided, will use stream_name
        exchange_name: Name of the exchange to use. If not provided, will use default exchange
        routing_key: Routing key for messages. If not provided, will use stream_name
        exchange_type: Type of exchange ('direct', 'fanout', 'topic', or 'headers')
        exchange_durable: Whether the exchange should survive broker restarts
        queue_durable: Whether the queue should survive broker restarts
        use_pool: Whether to use connection/channel pooling
        pool_size: Size of the connection/channel pool if use_pool is True

    Raises:
        ConfigurationError: If any configuration values are invalid
    """

    url: str
    queue_name: Optional[str] = None
    exchange_name: Optional[str] = None
    routing_key: Optional[str] = None
    exchange_type: Literal["direct", "fanout", "topic", "headers"] = "direct"
    exchange_durable: bool = True
    queue_durable: bool = True
    use_pool: bool = True
    pool_size: int = 2

    def __init__(self, url: str, **kwargs: Any) -> None:
        if not url or not isinstance(url, str):
            raise ConfigurationError("RabbitMQ URL must be a non-empty string")

        self.url = url
        self.queue_name = kwargs.pop("queue_name", None)
        self.exchange_name = kwargs.pop("exchange_name", None)
        self.routing_key = kwargs.pop("routing_key", None)
        self.exchange_type = kwargs.pop("exchange_type", "direct")

        if self.exchange_type not in ("direct", "fanout", "topic", "headers"):
            raise ConfigurationError(
                f"Invalid exchange_type '{self.exchange_type}'. "
                "Must be one of: direct, fanout, topic, headers"
            )

        self.exchange_durable = kwargs.pop("exchange_durable", True)
        self.queue_durable = kwargs.pop("queue_durable", True)
        self.use_pool = kwargs.pop("use_pool", True)
        self.pool_size = kwargs.pop("pool_size", 2)

        if self.use_pool and (not isinstance(self.pool_size, int) or self.pool_size < 1):
            raise ConfigurationError("pool_size must be a positive integer")

        # Allow additional attributes to be set
        for key, value in kwargs.items():
            setattr(self, key, value)
