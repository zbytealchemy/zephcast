"""Unit tests for consumer decorators."""


from zephcast.core.consumers import ConsumerConfig, ExecutorType, get_executor


def test_consumer_config_defaults() -> None:
    """Test ConsumerConfig default values."""
    config = ConsumerConfig()
    assert config.batch_size == 1
    assert config.batch_timeout == 1.0
    assert config.executor_type is None
    assert config.num_workers == 1
    assert config.auto_ack is True


def test_get_executor_thread() -> None:
    """Test thread executor creation."""
    executor = get_executor(ExecutorType.THREAD, 2)
    assert executor is not None
    executor.shutdown(wait=False)


def test_get_executor_process() -> None:
    """Test process executor creation."""
    executor = get_executor(ExecutorType.PROCESS, 2)
    assert executor is not None
    executor.shutdown(wait=False)


def test_get_executor_none() -> None:
    """Test no executor creation."""
    executor = get_executor(None, 2)
    assert executor is None
