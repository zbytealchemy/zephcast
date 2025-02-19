"""Unit tests for async retry functionality."""
import asyncio

from typing import Any
from unittest.mock import AsyncMock, Mock, call, patch

import pytest

from zephcast.aio.retry import AsyncRetryConfig, retry


class TestAsyncRetry:
    """Test suite for async retry functionality."""

    @pytest.mark.asyncio
    async def test_successful_execution_no_retry(self) -> None:
        """Test successful execution without any retries needed."""
        mock_fn = AsyncMock(return_value="success")
        config = AsyncRetryConfig(max_retries=3, retry_sleep=0.1)

        wrapped = retry(config)(mock_fn)
        result = await wrapped("arg1", kwarg1="value1")

        assert result == "success"
        mock_fn.assert_called_once_with("arg1", kwarg1="value1")

    @pytest.mark.asyncio
    async def test_retry_eventually_succeeds(self) -> None:
        """Test function that succeeds after multiple retries."""
        errors = [ValueError("error1"), ValueError("error2")]
        mock_fn = AsyncMock(side_effect=[*errors, "success"])
        on_retry = Mock()
        config = AsyncRetryConfig(max_retries=3, retry_sleep=0.1, backoff_factor=2.0, on_retry=on_retry)

        wrapped = retry(config)(mock_fn)
        result = await wrapped()

        assert result == "success"
        assert mock_fn.call_count == 3
        assert on_retry.call_count == 2
        on_retry.assert_has_calls([call(1, errors[0]), call(2, errors[1])])

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self) -> None:
        """Test function that fails after exhausting all retries."""
        error = ValueError("persistent error")
        mock_fn = AsyncMock(side_effect=error)
        on_retry = Mock()
        config = AsyncRetryConfig(max_retries=2, retry_sleep=0.1, backoff_factor=2.0, on_retry=on_retry)

        wrapped = retry(config)(mock_fn)

        with pytest.raises(ValueError) as exc_info:
            await wrapped()

        assert str(exc_info.value) == "persistent error"
        assert mock_fn.call_count == 3
        assert on_retry.call_count == 2

    @pytest.mark.asyncio
    async def test_specific_exceptions(self) -> None:
        """Test retry only occurs for specified exceptions."""
        mock_fn = AsyncMock(side_effect=[ValueError("retry"), TypeError("no retry")])
        config = AsyncRetryConfig(
            max_retries=3, retry_sleep=0.1, backoff_factor=2.0, exceptions=(ValueError,)
        )

        wrapped = retry(config)(mock_fn)

        with pytest.raises(TypeError) as exc_info:
            await wrapped()

        assert str(exc_info.value) == "no retry"
        assert mock_fn.call_count == 2

    @pytest.mark.asyncio
    async def test_backoff_timing(self) -> None:
        """Test exponential backoff timing between retries."""
        mock_fn = AsyncMock(side_effect=[ValueError, ValueError, "success"])
        mock_sleep = AsyncMock()
        config = AsyncRetryConfig(max_retries=3, retry_sleep=1.0, backoff_factor=2.0)

        with patch("asyncio.sleep", mock_sleep):
            wrapped = retry(config)(mock_fn)
            await wrapped()

        # First retry: ~1.0s, second retry: ~2.0s
        assert mock_sleep.call_count == 2
        # Allow for some timing variation
        assert abs(mock_sleep.call_args_list[0][0][0] - 1.0) < 0.2
        assert abs(mock_sleep.call_args_list[1][0][0] - 2.0) < 0.2

    @pytest.mark.asyncio
    async def test_condition_check(self) -> None:
        """Test retry based on result condition."""
        mock_fn = AsyncMock(side_effect=[1, 2, 3])
        config = AsyncRetryConfig(
            max_retries=3, retry_sleep=0.1, backoff_factor=2.0, condition=lambda x: x > 2
        )

        wrapped = retry(config)(mock_fn)
        with patch("asyncio.sleep", AsyncMock()):
            result = await wrapped()

        assert mock_fn.call_count == 3
        assert result == 3

    @pytest.mark.asyncio
    async def test_condition_check_with_exception(self) -> None:
        """Test retry with both condition check and exceptions."""
        mock_fn = AsyncMock(side_effect=[ValueError(), 1, 2, 3])
        config = AsyncRetryConfig(
            max_retries=4,
            retry_sleep=0.1,
            backoff_factor=2.0,
            condition=lambda x: x > 2,
            exceptions=(ValueError,),
        )

        wrapped = retry(config)(mock_fn)
        with patch("asyncio.sleep", AsyncMock()):
            result = await wrapped()

        assert mock_fn.call_count == 4
        assert result == 3

    @pytest.mark.asyncio
    async def test_retry_preserves_function_metadata(self) -> None:
        """Test retry decorator preserves function metadata."""

        async def test_fn(x: int, y: str) -> dict[str, Any]:
            """Test function docstring."""
            return {"x": x, "y": y}

        wrapped = retry(AsyncRetryConfig())(test_fn)

        assert wrapped.__name__ == "test_fn"
        assert wrapped.__doc__ == "Test function docstring."
        assert wrapped.__annotations__ == test_fn.__annotations__

    @pytest.mark.asyncio
    async def test_concurrent_retries(self) -> None:
        """Test multiple concurrent retried operations."""
        mock_fn = AsyncMock()
        mock_fn.side_effect = [
            ValueError("error1"),
            ValueError("error2"),
            "success1",
            ValueError("error3"),
            "success2",
            ValueError("error4"),
            "success3",
        ]

        config = AsyncRetryConfig(max_retries=3, retry_sleep=0.1)
        wrapped = retry(config)(mock_fn)

        with patch("asyncio.sleep", AsyncMock()):
            results = await asyncio.gather(wrapped("task1"), wrapped("task2"), wrapped("task3"))

        assert results == ["success1", "success2", "success3"]
        assert mock_fn.call_count == 7

    @pytest.mark.asyncio
    async def test_zero_retries(self) -> None:
        """Test behavior with zero retries configured."""
        mock_fn = AsyncMock(side_effect=ValueError("error"))
        config = AsyncRetryConfig(max_retries=0, retry_sleep=0.1)

        wrapped = retry(config)(mock_fn)

        with pytest.raises(ValueError) as exc_info:
            await wrapped()

        assert str(exc_info.value) == "error"
        mock_fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_nested_retries(self) -> None:
        """Test nested retry decorators."""
        inner_mock = AsyncMock(side_effect=[ValueError("inner"), "success"])
        outer_mock = AsyncMock(side_effect=[ValueError("outer"), "success"])

        inner_config = AsyncRetryConfig(max_retries=1, retry_sleep=0.1)
        outer_config = AsyncRetryConfig(max_retries=1, retry_sleep=0.1)

        @retry(outer_config)
        async def outer() -> Any:
            await outer_mock()
            return await inner()

        @retry(inner_config)
        async def inner() -> Any:
            return await inner_mock()

        with patch("asyncio.sleep", AsyncMock()):
            result = await outer()

        assert result == "success"
        assert outer_mock.call_count == 2
        assert inner_mock.call_count == 2
