import pytest
from unittest.mock import MagicMock
from setara_backend.handlers.auth import AuthHandler
from setara_backend.models import (
    TblUser,
    UserStatusEnum
)
from pyramid.httpexceptions import HTTPNotFound, HTTPUnauthorized


@pytest.fixture
def mock_session():
    """Provides a mock database session."""
    return MagicMock()


@pytest.fixture
def auth_handler(mock_session):
    """
    A fixture that creates an instance AuthHandler,
    injecting the clean db session.
    """
    return AuthHandler(mock_session)


@pytest.fixture
def mock_request():
    """Provides a mock Pyramid request object with all necessary sub-mocks."""
    request = MagicMock()
    request.validated = {
        'login_method': 'email',
        'user_identifier': 'test@example.com',
        'user_password': 'GoodPassword1!',
        'user_notification_token': 'fcm-token-123'
    }
    request.auth_service = MagicMock()
    request.redis_conn = MagicMock()
    request.environ = {
        'HTTP_X_REAL_IP': '8.8.8.8',
        'HTTP_USER_AGENT': 'Test Agent/1.0'
    }
    request.registry.settings = {'auth.expiration_seconds': 3600}
    return request


@pytest.fixture
def mock_active_user():
    """Provides a mock active user object."""
    user = MagicMock(spec=TblUser)
    user.user_id = 123
    user.user_status = UserStatusEnum.active
    user.user_password = 'hashed_password'
    user.user_role = 'staff'
    return user


class TestLoginHandler:
    """Test suite for the login handler."""

    def test_login_handler_success(self, mocker, auth_handler, mock_request, mock_active_user):
        """Tests the full successful login flow (the "happy path")."""
        # Setup
        auth_handler.user_repository = MagicMock()
        auth_handler.user_repository.get_user_by_identifier.return_value = mock_active_user
        mock_redis_repo = mocker.patch(
            'setara_backend.handlers.auth.RedisRepository')
        mocker.patch(
            'setara_backend.handlers.auth.get_location_from_ip',
            return_value={'city': 'Mountain View', 'loc': '37,-122'}
        )

        # Configure return values for our mocks
        mock_request.auth_service.check_password.return_value = True
        mock_redis_repo.return_value.get.return_value = None
        mock_request.auth_service.generate_access_token.return_value = 'a-new-jwt-token'

        # Action
        result = auth_handler.login_handler(mock_request)

        # Assert
        assert result['error'] is False
        assert result['message'] == 'Login berhasil'
        assert result['role'] == 'staff'
        assert result['role_id'] == None
        assert result['access_token'] == 'a-new-jwt-token'

        auth_handler.user_repository.get_user_by_identifier.assert_called_once()
        mock_request.auth_service.check_password.assert_called_once()
        mock_redis_repo.return_value.get.assert_called_with(
            f"auth_token:{mock_active_user.user_id}")
        assert mock_redis_repo.return_value.set.call_count == 2
        mock_redis_repo.return_value.set.assert_any_call(
            key=f"notification_token:{mock_active_user.user_id}",
            value='fcm-token-123',
            expire_seconds=3600
        )
        auth_handler.user_repository.update_user.assert_called_with(
            user=mock_active_user,
            new_data={'user_is_login': True}
        )

    def test_login_user_not_found(self, mocker, auth_handler, mock_request):
        """Tests that HTTPNotFound is raised if the user doesn't exist."""
        # Setup
        auth_handler.user_repository = MagicMock()
        auth_handler.user_repository.get_user_by_identifier.return_value = None
        mocker.patch('setara_backend.handlers.auth.RedisRepository')

        # Action & Assert
        with pytest.raises(HTTPNotFound, match='akun pengguna tidak ditemukan'):
            auth_handler.login_handler(mock_request)

    def test_login_user_inactive(self, mocker, auth_handler, mock_request, mock_active_user):
        """Tests that HTTPUnauthorized is raised for an inactive user."""
        # Setup
        auth_handler.user_repository = MagicMock()
        mock_active_user.user_status = UserStatusEnum.inactive
        auth_handler.user_repository.get_user_by_identifier.return_value = mock_active_user
        mocker.patch('setara_backend.handlers.auth.RedisRepository')

        # Action & Assert
        with pytest.raises(HTTPUnauthorized, match='akun anda belum aktif'):
            auth_handler.login_handler(mock_request)

    def test_login_incorrect_password(self, mocker, auth_handler, mock_request, mock_active_user):
        """Tests that HTTPUnauthorized is raised for a wrong password."""
        # Setup
        auth_handler.user_repository = MagicMock()
        auth_handler.user_repository.get_user_by_identifier.return_value = mock_active_user
        mocker.patch('setara_backend.handlers.auth.RedisRepository')
        mock_request.auth_service.check_password.return_value = False

        # Action & Assert
        with pytest.raises(HTTPUnauthorized, match='password anda tidak sesuai'):
            auth_handler.login_handler(mock_request)

    def test_login_already_logged_in(self, mocker, auth_handler, mock_request, mock_active_user):
        """Tests that HTTPUnauthorized is raised if a token already exists in Redis."""
        # Setup
        auth_handler.user_repository = MagicMock()
        auth_handler.user_repository.get_user_by_identifier.return_value = mock_active_user
        mock_redis_repo = mocker.patch(
            'setara_backend.handlers.auth.RedisRepository')
        mock_redis_repo.return_value.get.return_value = 'an-existing-token'
        mock_request.auth_service.check_password.return_value = True

        # Action & Assert
        with pytest.raises(HTTPUnauthorized, match='mohon logout terlebih dahulu'):
            auth_handler.login_handler(mock_request)


class TestLogoutHandler:
    """Test suite for the logout handler."""

    def test_logout_handler_success(self, mocker, auth_handler, mock_request, mock_active_user):
        """
        Tests that logout successfully deletes the auth and notification tokens from Redis.
        """
        # Setup
        user_id = 123
        mock_request.user = {'user_id': user_id}
        auth_handler.user_repository = MagicMock()
        auth_handler.user_repository.get_user_by_identifier.return_value = mock_active_user
        mock_redis_repo_class = mocker.patch(
            'setara_backend.handlers.auth.RedisRepository')
        mock_redis_instance = mock_redis_repo_class.return_value

        # Action
        result = auth_handler.logout_handler(mock_request)

        # Assert
        assert result == {
            "error": False,
            "message": "Logout berhasil"
        }

        mock_redis_repo_class.assert_called_once_with(mock_request.redis_conn)
        assert mock_redis_instance.delete.call_count == 2
        mock_redis_instance.delete.assert_any_call(f"auth_token:{user_id}")
        mock_redis_instance.delete.assert_any_call(
            f"notification_token:{user_id}")
        auth_handler.user_repository.update_user.assert_called_with(
            user=mock_active_user,
            new_data={'user_is_login': False}
        )
