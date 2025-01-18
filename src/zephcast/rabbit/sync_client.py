from collections.abc import Iterator
from typing import TYPE_CHECKING, Any, Optional

import pika

from zephcast.core.base import SyncMessagingClient
from zephcast.core.factory import register_client

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
    from pika.spec import Basic, BasicProperties


class SyncRabbitClient(SyncMessagingClient[str]):
    """Synchronous RabbitMQ client implementation."""

    def __init__(
        self,
        stream_name: str,
        host: str = "localhost",
        port: int = 5672,
        username: str = "guest",
        password: str = "guest",
        virtual_host: str = "/",
        **kwargs: Any,
    ) -> None:
        """Initialize RabbitMQ client.

        Args:
            stream_name: Queue name
            host: RabbitMQ host
            port: RabbitMQ port
            username: RabbitMQ username
            password: RabbitMQ password
            virtual_host: RabbitMQ virtual host
        """
        super().__init__(stream_name=stream_name, **kwargs)
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(username, password)
        self.virtual_host = virtual_host
        self.connection: Optional[BlockingConnection] = None
        self.channel: Optional[BlockingChannel] = None
        self._consumer_tag: Optional[str] = None

    def connect(self) -> None:
        """Establish a connection to RabbitMQ."""
        parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=self.credentials,
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.stream_name, durable=True)

    def send(self, message: str) -> None:
        """Send a message to the queue."""
        if self.channel is None:
            raise RuntimeError("RabbitMQ connection not established")

        self.channel.basic_publish(
            exchange="",
            routing_key=self.stream_name,
            body=message.encode(),
            properties=pika.BasicProperties(
                delivery_mode=2,
            ),
        )

    def receive(self) -> Iterator[str]:
        """Receive messages from the queue."""
        if not self.connection or not self.channel:
            raise RuntimeError("RabbitMQ connection not established")

        while True:
            method_frame: Basic.GetOk
            header_frame: BasicProperties
            body: bytes

            method_frame, header_frame, body = self.channel.basic_get(
                queue=self.stream_name, auto_ack=True
            )

            if method_frame:
                yield body.decode()
            else:
                self.connection.sleep(0.1)

    def close(self) -> None:
        """Close the RabbitMQ connection."""
        if self.channel is not None:
            if self._consumer_tag:
                self.channel.basic_cancel(self._consumer_tag)
            self.channel.close()
            self.channel = None

        if self.connection is not None:
            self.connection.close()
            self.connection = None


# Register the client
register_client("rabbitmq", "sync", SyncRabbitClient)
