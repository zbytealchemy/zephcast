"""Messaging client factory."""
from typing import Any, TypeVar, Union

T = TypeVar("T")
SyncBaseClient = TypeVar("SyncBaseClient")
AsyncBaseClient = TypeVar("AsyncBaseClient")

ClientType = Union[type[SyncBaseClient], type[AsyncBaseClient]]
_REGISTERED_CLIENTS: dict[str, dict[str, ClientType]] = {
    "sync": {},
    "async": {},
}


def register_client(name: str, client_type: str, client_class: ClientType) -> None:
    """Register a messaging client."""
    if client_type not in ("sync", "async"):
        raise ValueError("client_type must be either 'sync' or 'async'")

    _REGISTERED_CLIENTS[client_type][name] = client_class


def create_client(
    name: str,
    stream_name: str,
    is_async: bool = True,
    **kwargs: Any,
) -> Any:
    """Create a messaging client."""
    client_type = "async" if is_async else "sync"
    clients = _REGISTERED_CLIENTS[client_type]

    if name not in clients:
        available = ", ".join(clients.keys())
        raise ValueError(
            f"No {client_type} client registered for '{name}'. " f"Available clients: {available}"
        )

    client_class = clients[name]
    return client_class(stream_name=stream_name, **kwargs)
