"""Base mock client for testing."""

from zephcast.core.types import ConnectionConfig


class MockBaseClient:
    """Base class for mock clients."""

    def __init__(
        self,
        stream_name: str,
        connection_config: ConnectionConfig | None = None,
    ) -> None:
        """Initialize mock client."""
        self.stream_name = stream_name
        self.connection_config = connection_config
        self._connected = False
