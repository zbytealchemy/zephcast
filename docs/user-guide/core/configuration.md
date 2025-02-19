# Core Configuration

## Base Configuration Classes

### ConsumerConfig
Base configuration class for all consumers (sync and async):

```python
class ConsumerConfig:
    batch_size: int          # Number of messages to process at once
    batch_timeout: float     # Timeout for batch collection
    executor_type: Optional[ExecutorType]  # Thread or Process executor
    num_workers: int         # Number of workers for parallel processing
    auto_ack: bool          # Automatic message acknowledgment
```

### BrokerConfig
Base configuration for message broker connections:

```python
class BrokerConfig:
    connection_timeout: float    # Connection timeout in seconds
    operation_timeout: float     # Operation timeout in seconds
    max_connections: int         # Maximum number of connections
    tls_enabled: bool           # Enable TLS/SSL
    tls_verify: bool            # Verify TLS certificates
```