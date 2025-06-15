import pytest
import types
from marshmallow import (
    Schema,
    fields
)
from pyramid import testing
from pyramid.response import Response
from setara_backend.middleware.decorators import (
    secure_view, validate_form_schema
)
from pyramid.httpexceptions import (
    HTTPUnauthorized,
    HTTPForbidden,
    HTTPBadRequest,
    HTTPUnsupportedMediaType
)


@pytest.fixture
def pyramid_config():
    """Sets up a basic Pyramid testing configuration."""
    config = testing.setUp()
    yield config
    testing.tearDown()


@pytest.fixture
def dummy_request(pyramid_config):
    """Returns a Pyramid DummyRequest."""
    return testing.DummyRequest()


@pytest.fixture
def mock_view():
    """
    A mock view that tracks if it has been called.
    Returns a dictionary to inspect its state.
    """
    call_info = {"called": False}

    def view(request):
        call_info["called"] = True
        return Response("View was called successfully!")
    return view, call_info


class TestSecurityDecorator:
    def test_secure_view_with_class_based_view_context(dummy_request, mock_view):
        """
        Tests that the secure_view decorator correctly handles a class-based
        view context by finding the request on the view instance.
        """
        # Setup
        view_func, call_info = mock_view
        mock_view_instance = types.SimpleNamespace()
        mock_view_instance.request = dummy_request
        mock_view_instance.request.user = {'id': 1, 'user_role': 'admin'}
        decorated_view = secure_view(
            type='private', roles=['admin'])(view_func)

        # Action
        #   Call the decorated view with the mock instance to trigger the 'if' branch.
        decorated_view(mock_view_instance)

        # Assert
        # Check that authentication and authorization passed and the view was called.
        assert call_info["called"] is True

    def test_secure_view_public_allows_access(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        decorated_view = secure_view(type='public')(view_func)

        # Action
        response = decorated_view(dummy_request)

        # Assert
        assert call_info["called"] is True
        assert response.text == "View was called successfully!"

    def test_secure_view_private_unauthenticated_raises_unauthorized(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        dummy_request.user = None  # Simulate no authenticated user
        decorated_view = secure_view(type='private')(view_func)

        # Action & Assert
        with pytest.raises(HTTPUnauthorized):
            decorated_view(dummy_request)
        assert call_info["called"] is False

    def test_secure_view_private_authenticated_no_roles_succeeds(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        # Simulate an authenticated user
        dummy_request.user = {'id': 1, 'user_role': 'user'}
        decorated_view = secure_view(type='private')(
            view_func)  # No roles specified

        # Action
        decorated_view(dummy_request)

        # Assert
        assert call_info["called"] is True

    def test_secure_view_private_authorized_role_succeeds(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        dummy_request.user = {'id': 1, 'user_role': 'admin'}
        decorated_view = secure_view(roles=['admin', 'manager'])(view_func)

        # Action
        decorated_view(dummy_request)

        # Assert
        assert call_info["called"] is True

    def test_secure_view_private_unauthorized_role_raises_forbidden(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        dummy_request.user = {'id': 1, 'user_role': 'user'}
        decorated_view = secure_view(roles=['admin', 'manager'])(view_func)

        # Action & Assert
        with pytest.raises(HTTPForbidden):
            decorated_view(dummy_request)
        assert call_info["called"] is False


class SampleFormSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)


class TestValidationDecorator:
    def test_validate_schema_with_class_based_view_context(dummy_request, mock_view):
        """
        Tests that the decorator correctly handles a class-based view context
        by finding the request on the view instance.
        """
        # Setup
        view_func, call_info = mock_view
        dummy_request.POST = {'name': 'Test', 'email': 'test@example.com'}

        mock_view_instance = types.SimpleNamespace()
        mock_view_instance.request = dummy_request

        # Decorate the view function as usual.
        decorated_view = validate_form_schema(SampleFormSchema)(view_func)

        # Action
        decorated_view(mock_view_instance)

        # Assert
        # Check that the decorator found the request and the view was called.
        assert call_info["called"] is True

        # Check that the decorator correctly attached the validated data to the request.
        assert hasattr(dummy_request, 'validated')
        assert dummy_request.validated['name'] == 'Test'

    def test_validate_schema_success(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        dummy_request.POST = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
        decorated_view = validate_form_schema(SampleFormSchema)(view_func)

        # Action
        decorated_view(dummy_request)

        # Assert
        assert call_info["called"] is True
        assert hasattr(dummy_request, 'validated')
        assert dummy_request.validated['name'] == 'John Doe'

    def test_validate_schema_invalid_data_raises_bad_request(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        # Missing required 'email' field
        dummy_request.POST = {'name': 'John Doe'}
        decorated_view = validate_form_schema(SampleFormSchema)(view_func)

        # Action & Assert
        with pytest.raises(HTTPBadRequest) as excinfo:
            decorated_view(dummy_request)

        assert call_info["called"] is False
        # Check that the exception body contains the Marshmallow error message
        assert 'email' in excinfo.value.message
        assert 'Missing data for required field.' in excinfo.value.message['email']

    def test_validate_schema_no_form_data_raises_unsupported_media_type(self, dummy_request, mock_view):
        # Setup
        view_func, call_info = mock_view
        dummy_request.POST = {}  # Simulate an empty form submission
        decorated_view = validate_form_schema(SampleFormSchema)(view_func)

        # Action & Assert
        with pytest.raises(HTTPUnsupportedMediaType):
            decorated_view(dummy_request)
        assert call_info["called"] is False
