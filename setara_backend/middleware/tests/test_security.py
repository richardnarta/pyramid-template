import pytest
import jwt
from setara_backend.middleware.security import JWTAuthenticationPolicy
from pyramid import testing
from pyramid.interfaces import IAuthenticationPolicy
from zope.interface.verify import verifyObject
from unittest.mock import MagicMock


@pytest.fixture
def auth_policy():
    """A fixture for a JWTAuthenticationPolicy instance."""
    return JWTAuthenticationPolicy('secret', ['HS256'], 3600)


@pytest.fixture
def dummy_request():
    """A fixture for a Pyramid DummyRequest."""
    return testing.DummyRequest()


class TestJWTSecurity:
    def test_policy_implements_interface(self, auth_policy):
        """Checks that our policy correctly implements the Zope interface."""
        assert verifyObject(IAuthenticationPolicy, auth_policy) is True

    def test_unauthenticated_userid_no_token(self, auth_policy, dummy_request):
        """Tests the case where no token is in the request headers."""
        assert auth_policy.unauthenticated_userid(dummy_request) is None

    def test_unauthenticated_userid_invalid_token(self, auth_policy, dummy_request):
        """Tests when the token is present but invalid, causing a PyJWTError."""
        dummy_request.headers['Authorization'] = 'Bearer invalid-token'
        mock_auth_service = MagicMock()
        mock_auth_service.get_user_from_access_token.side_effect = jwt.PyJWTError
        dummy_request.auth_service = mock_auth_service

        assert auth_policy.unauthenticated_userid(dummy_request) is None

    def test_unauthenticated_userid_token_not_in_redis(self, auth_policy, dummy_request):
        """Tests when the token is valid but doesn't match the one in Redis."""
        token = 'valid-token'
        claims = {'user_id': 'user123', 'user_role': 'user'}
        dummy_request.headers['Authorization'] = f'Bearer {token}'

        # Mock auth service to return claims
        mock_auth_service = MagicMock()
        mock_auth_service.get_user_from_access_token.return_value = claims
        dummy_request.auth_service = mock_auth_service

        # Mock Redis to return a different token (or None)
        mock_redis_conn = MagicMock()
        mock_redis_conn.get.return_value = 'some-other-token'
        dummy_request.redis_conn = mock_redis_conn

        # Action
        result = auth_policy.unauthenticated_userid(dummy_request)

        # Assert
        assert result is None
        assert dummy_request.user is None
        mock_redis_conn.get.assert_called_with('auth_token:user123')

    def test_unauthenticated_userid_success(self, auth_policy, dummy_request, mocker):
        """Tests the happy path: valid token that matches the one in Redis."""
        token = 'the-correct-token'
        claims = {'user_id': 'user123', 'user_role': 'user'}
        dummy_request.headers['Authorization'] = f'Bearer {token}'

        # Mock auth service
        mock_auth_service = MagicMock()
        mock_auth_service.get_user_from_access_token.return_value = claims
        dummy_request.auth_service = mock_auth_service

        # Mock Redis to return the *same* token
        dummy_request.redis_conn = MagicMock()
        mock_redis_repo = MagicMock()
        mock_redis_repo.get.return_value = token
        mocker.patch('setara_backend.middleware.security.RedisRepository',
                     return_value=mock_redis_repo)

        # Action
        result = auth_policy.unauthenticated_userid(dummy_request)

        # Assert
        assert result == 'user123'
        assert dummy_request.user == claims
        mock_redis_repo.get.assert_called_with('auth_token:user123')
        # Check that the expiration was reset
        mock_redis_repo.set.assert_called_with(
            'auth_token:user123', token, expire_seconds=3600)
