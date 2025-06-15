import pytest
import jwt
from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock
from setara_backend.services import AuthService
from setara_backend.models import TblUser


@pytest.fixture
def settings():
    """Provides mock settings for the AuthService."""
    return {'auth.secret': 'test-secret-key', 'auth.algorithm': 'HS256'}


@pytest.fixture
def auth_service(settings):
    """Provides a ready instance of AuthService."""
    return AuthService(settings)


@pytest.fixture
def mock_user():
    """Provides a mock user object for testing."""
    user = MagicMock(spec=TblUser)
    user.id = 123
    user.username = 'testuser'
    return user


class TestAuthService:
    """Test suite for the AuthService class."""

    def test_hash_password_is_verifiable(self, auth_service):
        """
        Tests that hash_password produces a valid bcrypt hash that can be
        verified by check_password.
        """
        # Setup
        plain_password = 'my_super_secret_password'

        # Action
        hashed_password = auth_service.hash_password(plain_password)

        # Assert
        assert isinstance(hashed_password, str)
        assert auth_service.check_password(
            plain_password, hashed_password) is True

    def test_check_password_failure(self, auth_service):
        """
        Tests that check_password returns False for an incorrect password.
        """
        # Setup
        correct_password = 'correct_password'
        wrong_password = 'wrong_password'

        # Action
        hashed_password = auth_service.hash_password(correct_password)

        # Assert
        assert auth_service.check_password(
            wrong_password, hashed_password) is False

    # REFACTORED to use the 'mocker' fixture
    def test_generate_access_token(self, mocker, auth_service, mock_user, settings):
        """
        Tests that a JWT access token is generated with the correct payload.
        """
        # Setup
        # Mock dependencies using mocker.patch
        mock_datetime = mocker.patch('setara_backend.services.auth.datetime')
        mock_user_mapper = mocker.patch(
            'setara_backend.services.auth.UserMapper')

        # Mock the current time to get a predictable 'iat' claim
        mock_now = datetime(2025, 6, 12, 12, 0, 0, tzinfo=UTC)
        mock_datetime.now.return_value = mock_now

        # Mock the payload returned by the UserMapper
        user_payload_from_mapper = {
            'user_id': mock_user.id, 'username': mock_user.username, 'role': 'user'}
        mock_user_mapper.db_to_access_token.return_value = user_payload_from_mapper

        # Provide an additional payload from the view/controller
        extra_payload = {'session_id': 'xyz-123'}

        # Action
        token = auth_service.generate_access_token(mock_user, extra_payload)

        # Assert
        mock_user_mapper.db_to_access_token.assert_called_with(mock_user)
        decoded_payload = jwt.decode(
            token,
            settings['auth.secret'],
            algorithms=[settings['auth.algorithm']],
            options={"verify_iat": False}
        )

        assert decoded_payload['user_id'] == mock_user.id
        assert decoded_payload['username'] == mock_user.username
        assert decoded_payload['role'] == 'user'
        assert decoded_payload['session_id'] == 'xyz-123'
        assert decoded_payload['iat'] == int(mock_now.timestamp())

    def test_get_user_from_access_token_success(self, auth_service, settings):
        """
        Tests successful decoding of a valid access token.
        """
        # Setup
        payload = {'user_id': 456, 'username': 'another_user'}
        token = jwt.encode(
            payload, settings['auth.secret'], algorithm=settings['auth.algorithm'])

        # Action
        decoded_payload = auth_service.get_user_from_access_token(token)

        # Assert
        assert decoded_payload == payload

    def test_get_user_from_access_token_invalid_signature(self, auth_service, settings):
        """
        Tests that an InvalidTokenError is raised for a token with a bad signature.
        """
        # Setup
        payload = {'user_id': 456}
        # Encode with the wrong secret
        token = jwt.encode(payload, 'this-is-the-wrong-secret',
                           algorithm=settings['auth.algorithm'])

        # Action & Assert
        with pytest.raises(jwt.InvalidTokenError):
            auth_service.get_user_from_access_token(token)

    def test_get_user_from_access_token_expired(self, auth_service, settings):
        """
        Tests that an ExpiredSignatureError is raised for an expired token.
        """
        # Setup
        payload = {
            'user_id': 456,
            # Set the expiration time to 10 minutes in the past
            'exp': datetime.now(UTC) - timedelta(minutes=10)
        }
        token = jwt.encode(
            payload, settings['auth.secret'], algorithm=settings['auth.algorithm'])

        # Action & Assert
        with pytest.raises(jwt.ExpiredSignatureError):
            auth_service.get_user_from_access_token(token)
