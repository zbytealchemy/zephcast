"""Synchronous RabbitMQ client."""
from zephcast.sync.rabbit.client import RabbitClient
from zephcast.sync.rabbit.types import RabbitConfig

__all__ = ["RabbitClient", "RabbitConfig"]
