"""Type definitions for Kafka sync client."""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class KafkaConfig:
    """Kafka connection configuration."""

    bootstrap_servers: str
    group_id: Optional[str] = None
    client_id: Optional[str] = None
    auto_offset_reset: str = "latest"
    enable_auto_commit: bool = True

    def __init__(self, bootstrap_servers: str, **kwargs: Any) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.group_id = kwargs.pop("group_id", None)
        self.client_id = kwargs.pop("client_id", None)
        self.auto_offset_reset = kwargs.pop("auto_offset_reset", "latest")
        self.enable_auto_commit = kwargs.pop("enable_auto_commit", True)
        for key, value in kwargs.items():
            setattr(self, key, value)
