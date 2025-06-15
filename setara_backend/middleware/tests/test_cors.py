import pytest
from pyramid import testing
from pyramid.response import Response
from setara_backend.middleware.cors import cors_tween_factory


@pytest.fixture
def pyramid_config():
    """A fixture that sets up and tears down a Pyramid testing configuration."""
    config = testing.setUp()
    yield config
    testing.tearDown()


@pytest.fixture
def dummy_handler():
    """A fixture that creates a simple dummy handler returning a basic response."""
    def handler(request):
        return Response('OK from handler')
    return handler


class TestCORS:
    def test_options_preflight_request(self, pyramid_config, dummy_handler):
        """
        Tests that an OPTIONS request gets the correct pre-flight CORS headers
        and does not call the next handler in the chain.
        """
        # Setup
        tween = cors_tween_factory(dummy_handler, pyramid_config.registry)
        request = testing.DummyRequest(method='OPTIONS')

        # Action
        response = tween(request)

        # Assert
        # Check for the correct pre-flight headers
        assert response.headers.get('Access-Control-Allow-Origin') == '*'
        assert response.headers.get(
            'Access-Control-Allow-Methods') == 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        assert response.headers.get(
            'Access-Control-Allow-Headers') == 'Content-Type, Authorization'
        assert response.headers.get('Access-Control-Max-Age') == '3600'

        # Assert that the handler was not called (body is not the handler's response)
        assert response.text != 'OK from handler'
        # And the response body is empty as expected for a pre-flight
        assert response.text == ''

    def test_non_options_get_request(self, pyramid_config, dummy_handler):
        """
        Tests that a non-OPTIONS request (e.g., GET) gets the correct CORS headers
        after the main handler has been called.
        """
        # Setup
        tween = cors_tween_factory(dummy_handler, pyramid_config.registry)
        request = testing.DummyRequest(method='GET', path='/')

        # Acion
        response = tween(request)

        # Assert
        # Check that the handler was called and its response was used
        assert response.text == 'OK from handler'

        # Assert: Check that the CORS headers have been added to the response
        assert response.headers.get('Access-Control-Allow-Origin') == '*'
        assert response.headers.get(
            'Access-Control-Allow-Methods') == 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        assert response.headers.get(
            'Access-Control-Allow-Headers') == 'Content-Type, Authorization'
        # 'Access-Control-Max-Age' should not be present for non-OPTIONS requests
        assert 'Access-Control-Max-Age' not in response.headers
