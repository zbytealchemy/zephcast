"""Messaging client factory."""

from typing import Any, Union

from .base import AsyncMessagingClient, SyncMessagingClient

ClientType = Union[type[SyncMessagingClient], type[AsyncMessagingClient]]
_REGISTERED_CLIENTS: dict[str, dict[str, ClientType]] = {
    "sync": {},
    "async": {},
}


def register_client(name: str, client_type: str, client_class: ClientType) -> None:
    """Register a messaging client.

    Args:
        name: Name of the client (e.g., 'redis', 'rabbitmq')
        client_type: Type of client ('sync' or 'async')
        client_class: Client class to register
    """
    if client_type not in ("sync", "async"):
        raise ValueError("client_type must be either 'sync' or 'async'")

    _REGISTERED_CLIENTS[client_type][name] = client_class


def create_client(
    name: str,
    stream_name: str,
    is_async: bool = True,
    **kwargs: Any,
) -> Union[SyncMessagingClient, AsyncMessagingClient]:
    """Create a messaging client.

    Args:
        name: Name of the client (e.g., 'redis', 'rabbitmq')
        stream_name: Name of the stream/queue/topic
        is_async: Whether to create an async client
        **kwargs: Additional arguments to pass to the client

    Returns:
        A messaging client instance
    """
    client_type = "async" if is_async else "sync"
    clients = _REGISTERED_CLIENTS[client_type]

    if name not in clients:
        available = ", ".join(clients.keys())
        raise ValueError(
            f"No {client_type} client registered for '{name}'. " f"Available clients: {available}"
        )

    client_class = clients[name]
    return client_class(stream_name=stream_name, **kwargs)
