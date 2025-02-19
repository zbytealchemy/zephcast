# Core Types

## Message Types

```python
from typing import TypeVar, Generic, Dict, Any

Message = TypeVar('Message')
Headers = Dict[str, str]

class MessageEnvelope(Generic[Message]):
    payload: Message
    headers: Headers
    timestamp: float
    message_id: str
```

## Callback Types

```python
from typing import Callable, Awaitable, Union

SyncCallback = Callable[[Message], None]
AsyncCallback = Callable[[Message], Awaitable[None]]
ConsumerCallback = Union[SyncCallback, AsyncCallback]
```

## Exception Types

```python
class BrokerError(Exception):
    """Base class for all broker-related errors"""

class ConnectionError(BrokerError):
    """Connection-related errors"""

class ConsumerError(BrokerError):
    """Consumer-related errors"""
```