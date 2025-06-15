import pytest
from setara_backend.models import TblUser
from unittest.mock import MagicMock
from datetime import (
    datetime,
    UTC
)
from setara_backend.utils import UserMapper


@pytest.fixture
def mock_db_user():
    """Provides a mock user object for testing."""
    user = MagicMock(spec=TblUser)

    dict_data = {
        'user_id': 123,
        'user_username': 'testuser',
        'user_password': 'a_secret_hash_to_be_deleted',
        'user_role': 'admin',
        'user_approved_at': datetime(2025, 6, 10, 10, 0, 0, tzinfo=UTC),
        'user_updated_at': datetime(2025, 6, 10, 10, 0, 0, tzinfo=UTC),
        'user_created_at': datetime(2025, 6, 10, 10, 0, 0, tzinfo=UTC),
        '_sa_instance_state': 'some_sqlalchemy_state_object'
    }

    user.__dict__.update(dict_data)

    user.user_status = MagicMock()
    user.user_status.value = 'active'
    return user


class TestUserMapper:
    """Test suite for the UserMapper static methods."""

    def test_db_to_access_token_success(self, mock_db_user):
        """
        Tests the happy path where a valid user object is mapped correctly.
        """
        # Action
        result = UserMapper.db_to_access_token(mock_db_user)

        # Assert
        # Check that sensitive fields were removed
        assert 'user_password' not in result
        assert '_sa_instance_state' not in result

        # Check that special values were correctly transformed
        assert result['user_status'] == 'active'
        assert result['user_created_at'] == '2025-06-10T10:00:00+00:00'

    def test_db_to_access_token_with_none_user(self):
        """
        Tests that passing None to the mapper returns an empty dictionary.
        """
        # Action
        result = UserMapper.db_to_access_token(None)

        # Assert
        assert result == {}

    def test_db_to_access_token_missing_datetime_fails_gracefully(self, mock_db_user):
        """
        Tests that an exception during mapping (e.g., a missing attribute)
        is caught and returns an empty dictionary.
        """
        # Setup
        del mock_db_user.user_created_at

        # Action
        result = UserMapper.db_to_access_token(mock_db_user)

        # Assert
        assert result == {}

    def test_db_to_access_token_missing_password_key_fails_gracefully(self, mock_db_user):
        """
        Tests that a KeyError when deleting a non-existent key is handled.
        """
        # Setup
        del mock_db_user.user_password

        # Action
        result = UserMapper.db_to_access_token(mock_db_user)

        # Assert
        assert result == {}
