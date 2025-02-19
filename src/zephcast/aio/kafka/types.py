"""Type definitions for Kafka async client."""
from dataclasses import dataclass
from typing import Any, Literal, Optional

from zephcast.core.exceptions import ConfigurationError


@dataclass
class KafkaConfig:
    """Kafka connection configuration.

    Args:
        bootstrap_servers: Comma-separated list of Kafka broker addresses
        group_id: Consumer group ID for consumer groups functionality
        client_id: Client identifier for tracking
        auto_offset_reset: What to do when there is no initial offset ('latest' or 'earliest')
        enable_auto_commit: Whether to auto-commit consumer offsets

    Raises:
        ConfigurationError: If any configuration values are invalid
    """

    bootstrap_servers: str
    group_id: Optional[str] = None
    client_id: Optional[str] = None
    auto_offset_reset: Literal["latest", "earliest"] = "latest"
    enable_auto_commit: bool = True

    def __init__(self, bootstrap_servers: str, **kwargs: Any) -> None:
        if not bootstrap_servers or not isinstance(bootstrap_servers, str):
            raise ConfigurationError("bootstrap_servers must be a non-empty string")

        self.bootstrap_servers = bootstrap_servers

        # Optional group_id and client_id
        self.group_id = kwargs.pop("group_id", None)
        self.client_id = kwargs.pop("client_id", None)

        # Validate auto_offset_reset
        self.auto_offset_reset = kwargs.pop("auto_offset_reset", "latest")
        if self.auto_offset_reset not in ("latest", "earliest"):
            raise ConfigurationError(
                f"Invalid auto_offset_reset '{self.auto_offset_reset}'. " "Must be one of: latest, earliest"
            )

        # Validate enable_auto_commit
        self.enable_auto_commit = kwargs.pop("enable_auto_commit", True)
        if not isinstance(self.enable_auto_commit, bool):
            raise ConfigurationError("enable_auto_commit must be a boolean value")

        # Allow additional attributes to be set
        for key, value in kwargs.items():
            setattr(self, key, value)
