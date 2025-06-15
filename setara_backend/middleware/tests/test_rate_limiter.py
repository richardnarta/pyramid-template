import pytest
from pyramid.response import Response
from pyramid import testing
from setara_backend.middleware.rate_limiter import rate_limiter_tween_factory
from pyramid.httpexceptions import HTTPTooManyRequests
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_handler():
    """A fixture that creates a simple mock handler to track if it was called."""
    call_info = {"called": False}

    def handler(request):
        call_info["called"] = True
        return Response("OK")
    return handler, call_info


@pytest.fixture
def dummy_request():
    """A fixture for a basic Pyramid DummyRequest."""
    return testing.DummyRequest()


class TestRateLimiter:
    def test_rate_limiter_options_request_bypasses_check(self, dummy_request, mock_handler):
        """
        Tests that an OPTIONS request is not rate-limited and calls the handler.
        """
        # Setup
        handler_func, call_info = mock_handler
        tween = rate_limiter_tween_factory(handler_func, None)
        dummy_request.method = 'OPTIONS'
        # No redis_conn is needed as it should not be touched

        # Action
        tween(dummy_request)

        # Assert
        assert call_info["called"] is True

    def test_rate_limiter_under_limit_succeeds(self, dummy_request, mock_handler):
        """
        Tests that a request within the limit is allowed and calls the handler.
        """
        # Setup
        handler_func, call_info = mock_handler
        tween = rate_limiter_tween_factory(handler_func, None)
        dummy_request.method = 'GET'
        dummy_request.environ['REMOTE_ADDR'] = '192.168.1.100'

        # Mock the pipeline and its return value (request_count=5, which is < 10)
        mock_pipeline = MagicMock()
        mock_pipeline.execute.return_value = (5, True)

        # Mock the redis connection to return the mock pipeline
        mock_redis_conn = MagicMock()
        mock_redis_conn.pipeline.return_value = mock_pipeline

        # Attach the mock redis connection to the request
        dummy_request.redis_conn = mock_redis_conn

        # Action
        tween(dummy_request)

        # Assert
        assert call_info["called"] is True
        mock_redis_conn.pipeline.assert_called_once()
        mock_pipeline.incr.assert_called_with('rate_limit:192.168.1.100')
        mock_pipeline.expire.assert_called_with('rate_limit:192.168.1.100', 1)
        mock_pipeline.execute.assert_called_once()

    def test_rate_limiter_over_limit_raises_exception(self, dummy_request, mock_handler):
        """
        Tests that a request exceeding the limit raises HTTPTooManyRequests
        and does NOT call the handler.
        """
        # Setup
        handler_func, call_info = mock_handler
        tween = rate_limiter_tween_factory(handler_func, None)
        dummy_request.method = 'POST'
        dummy_request.environ['REMOTE_ADDR'] = '192.168.1.100'

        # Mock the pipeline to return a count of 11 (which is > 10)
        mock_pipeline = MagicMock()
        mock_pipeline.execute.return_value = (11, True)  # Exceeds limit of 10

        mock_redis_conn = MagicMock()
        mock_redis_conn.pipeline.return_value = mock_pipeline
        dummy_request.redis_conn = mock_redis_conn

        # Action & Assert
        with pytest.raises(HTTPTooManyRequests) as excinfo:
            tween(dummy_request)

        assert call_info["called"] is False
        assert excinfo.value.json_body['message'] == "Rate limit exceeded"

    def test_rate_limiter_uses_fallback_ip(self, dummy_request, mock_handler):
        """
        Tests that the tween uses the fallback IP '127.0.0.1' if REMOTE_ADDR is missing.
        """
        # Setup
        handler_func, call_info = mock_handler
        tween = rate_limiter_tween_factory(handler_func, None)
        dummy_request.method = 'GET'

        mock_pipeline = MagicMock()
        mock_pipeline.execute.return_value = (1, True)  # Under the limit

        mock_redis_conn = MagicMock()
        mock_redis_conn.pipeline.return_value = mock_pipeline
        dummy_request.redis_conn = mock_redis_conn

        # Action
        tween(dummy_request)

        # Assert
        assert call_info["called"] is True
        mock_pipeline.incr.assert_called_with('rate_limit:127.0.0.1')
