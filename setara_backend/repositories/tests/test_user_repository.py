from setara_backend.repositories.user import UserRepository
from setara_backend.models.user import TblUser, UserStatusEnum
from datetime import datetime
import pytest


@pytest.fixture
def test_user(dbsession) -> TblUser:
    """
    A fixture that creates a standard user, adds it to the database,
    and returns the user object within an isolated transaction.
    """
    user = TblUser(
        user_phone='+6281211114444',
        user_username='john',
        user_email='john@example.com',
        user_name='John Doe',
        user_password='hashed_password_123',
        user_is_verified=True,
        user_is_login=False,
        user_role='admin_super',
        user_approved_at=datetime.now(),
        user_status=UserStatusEnum.active
    )
    dbsession.add(user)
    dbsession.flush()
    return user


@pytest.fixture
def user_repo(dbsession) -> UserRepository:
    """
    Provides an instance of UserRepository initialized with a clean
    database session for each test function.
    """
    return UserRepository(dbsession)


class TestGetUser:
    """Tests for retrieving users."""

    def test_get_unregistered_user(self, user_repo: UserRepository):
        """Tests that searching for a user that doesn't exist returns None."""
        # Action
        invalid_user = user_repo.get_user_by_identifier(
            identifier_type='phone',
            user_identifier='+6281200000000'
        )
        # Assert
        assert invalid_user is None

    def test_get_user_by_phone(self, user_repo: UserRepository, test_user: TblUser):
        """Tests retrieving a user by their phone number."""
        # Action
        found_user = user_repo.get_user_by_identifier(
            identifier_type='phone',
            user_identifier=test_user.user_phone
        )
        # Assert
        assert found_user is not None
        assert found_user.user_phone == test_user.user_phone

    def test_get_user_by_username(self, user_repo: UserRepository, test_user: TblUser):
        """Tests retrieving a user by their username."""
        # Action
        found_user = user_repo.get_user_by_identifier(
            identifier_type='username',
            user_identifier=test_user.user_username
        )
        # Assert
        assert found_user is not None
        assert found_user.user_username == test_user.user_username

    def test_get_user_by_email(self, user_repo: UserRepository, test_user: TblUser):
        """Tests retrieving a user by their email."""
        # Action
        found_user = user_repo.get_user_by_identifier(
            identifier_type='email',
            user_identifier=test_user.user_email
        )
        # Assert
        assert found_user is not None
        assert found_user.user_email == test_user.user_email

    def test_get_user_by_unknown_type(self, user_repo: UserRepository, test_user: TblUser):
        """Tests retrieving a user by their email."""
        # Action
        found_user = user_repo.get_user_by_identifier(
            identifier_type='id',
            user_identifier=test_user.user_id
        )
        # Assert
        assert found_user is not None
        assert found_user.user_id == test_user.user_id


class TestUpdateUser:
    """Tests for updating users."""

    def test_update_invalid_user(self, user_repo: UserRepository):
        """Tests that attempting to update a None user object returns False."""
        # Action
        update_status = user_repo.update_user(
            user=None,
            new_data={'user_name': 'New Name'}
        )
        # Assert
        assert update_status is False

    def test_update_user(self, user_repo: UserRepository, test_user: TblUser):
        """Tests that a user's data can be successfully updated."""
        # Setup
        new_phone_number = '+6281211113333'
        original_username = test_user.user_username

        # Action
        update_status = user_repo.update_user(
            user=test_user,
            new_data={
                'user_phone': new_phone_number,
                'user_name': 'Johnathan Doe'
            }
        )

        # Assert
        assert update_status is True
        # Verify the changes were made to the object in the session
        assert test_user.user_phone == new_phone_number
        assert test_user.user_name == 'Johnathan Doe'
        # Verify that fields not in the update data were NOT changed
        assert test_user.user_username == original_username
