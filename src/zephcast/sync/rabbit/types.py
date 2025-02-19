"""Type definitions for RabbitMQ sync client."""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class RabbitConfig:
    """RabbitMQ connection configuration."""

    url: str
    queue_name: Optional[str] = None
    exchange_name: Optional[str] = None
    routing_key: Optional[str] = None
    exchange_type: str = "direct"
    exchange_durable: bool = True
    queue_durable: bool = True
    auto_delete: bool = False
    prefetch_count: int = 1

    def __init__(self, url: str, **kwargs: Any) -> None:
        """Initialize RabbitMQ configuration.

        Args:
            url: RabbitMQ connection URL
            **kwargs: Additional configuration options
        """
        self.url = url
        self.queue_name = kwargs.pop("queue_name", None)
        self.exchange_name = kwargs.pop("exchange_name", None)
        self.routing_key = kwargs.pop("routing_key", None)
        self.exchange_type = kwargs.pop("exchange_type", "direct")
        self.exchange_durable = kwargs.pop("exchange_durable", True)
        self.queue_durable = kwargs.pop("queue_durable", True)
        self.auto_delete = kwargs.pop("auto_delete", False)
        self.prefetch_count = kwargs.pop("prefetch_count", 1)

        # Allow for additional custom attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
