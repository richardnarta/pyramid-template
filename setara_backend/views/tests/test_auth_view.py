import pytest
from requests_toolbelt.multipart.encoder import MultipartEncoder
from setara_backend.models import (
    TblUser,
    UserStatusEnum
)
from datetime import datetime


@pytest.fixture
def test_user(dbsession) -> TblUser:
    """
    A fixture that creates a standard user, adds it to the database,
    and returns the user object within an isolated transaction.
    """
    user = TblUser(
        user_phone='+6212345674567',
        user_username='john',
        user_email='john@example.com',
        user_name='John Doe',
        user_password='$2a$10$3D3/fv1EyrS5y7VQYEGL8u3CbTKm1swb4gWzJEQWqgkN3j55pB2gy',
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
def access_token(dbsession, redis_client, test_user: TblUser):
    from setara_backend.services.auth import AuthService
    auth_service = AuthService(
        {'auth.secret': 'secret', 'auth.algorithm': 'HS256'})

    TblUser(
        user_id=test_user.user_id,
        user_phone='+6212345674567',
        user_username='john',
        user_email='john@example.com',
        user_name='John Doe',
        user_password='$2a$10$3D3/fv1EyrS5y7VQYEGL8u3CbTKm1swb4gWzJEQWqgkN3j55pB2gy',
        user_is_verified=True,
        user_is_login=False,
        user_role='admin_super',
        user_approved_at=datetime.now(),
        user_status=UserStatusEnum.active
    )

    token = auth_service.generate_access_token(
        user=test_user,
        payload={}
    )

    redis_client.set(name=f'auth_token:{test_user.user_id}', value=token)
    return token


class TestAuthView:
    class TestLogin:
        def test_login_success(self, testapp, dbsession, redis_client, test_user: TblUser):
            # Setup
            payload = MultipartEncoder(
                fields={
                    'login_method': 'phone',
                    'user_identifier': '+6212345674567',
                    'user_password': 'Test12345!',
                    'user_notification_token': 'notification_token'
                }
            )

            # Action
            response = testapp.post(
                '/auth/login',
                params=payload.to_string(),
                headers={'Content-Type': payload.content_type},
                status=201
            )

            # Assert
            assert response.json['error'] == False
            assert response.json['message'] == 'Login berhasil'
            assert response.json['role'] == test_user.user_role
            assert response.json['role_id'] == None
            assert response.json['access_token'] == \
                redis_client.get(
                    f'auth_token:{test_user.user_id}').decode('utf-8')

        def test_login_fail_user_not_found(self, testapp, dbsession, redis_client):
            # Setup
            payload = MultipartEncoder(
                fields={
                    'login_method': 'phone',
                    'user_identifier': '+6212345674567',
                    'user_password': 'Test12345!',
                    'user_notification_token': 'notification_token'
                }
            )

            # Action
            response = testapp.post(
                '/auth/login',
                params=payload.to_string(),
                headers={'Content-Type': payload.content_type},
                status=404
            )

            # Assert
            assert response.json['error'] == True
            assert response.json['message'] == 'akun pengguna tidak ditemukan'

        def test_login_fail_bad_payload(self, testapp, dbsession, redis_client):
            # Setup
            payload = MultipartEncoder(
                fields={
                    'user_identifier': '+6212345674567',
                    'user_password': 'Test12345!',
                    'user_notification_token': 'notification_token'
                }
            )

            # Action
            response = testapp.post(
                '/auth/login',
                params=payload.to_string(),
                headers={'Content-Type': payload.content_type},
                status=400
            )

            # Assert
            assert response.json['error'] == True
            assert 'message' in response.json

    class TestLogout:
        def test_logout_success(self, testapp, dbsession, redis_client, access_token, test_user):
            # Setup
            headers = {
                'Authorization': f'Bearer {access_token}'
            }

            # Action
            response = testapp.get(
                '/auth/logout',
                headers=headers,
                status=200
            )

            # Assert
            assert response.json['error'] == False
            assert response.json['message'] == 'Logout berhasil'
            assert redis_client.get(f'auth_token:{test_user.user_id}') == None

        def test_logout_fail_invalid_access_token(self, testapp, dbsession, redis_client):
            # Action
            response = testapp.get(
                '/auth/logout',
                status=401
            )

            # Assert
            assert response.json['error'] == True
            assert response.json['message'] == 'missing/invalid token'
