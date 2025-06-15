from sqlalchemy.orm import Session
from setara_backend.repositories import (
    RedisRepository,
    UserRepository
)
from setara_backend.models import UserStatusEnum
from setara_backend.utils import get_location_from_ip
from pyramid.httpexceptions import HTTPNotFound, HTTPUnauthorized


class AuthHandler:
    def __init__(self, session: Session):
        self.user_repository = UserRepository(session)

    def login_handler(
        self,
        request
    ) -> dict:
        payload = request.validated
        auth_service = request.auth_service
        redis_repository = RedisRepository(request.redis_conn)

        # User availability check
        user = self.user_repository.get_user_by_identifier(
            identifier_type=payload['login_method'],
            user_identifier=payload['user_identifier'],
            user_status=[
                UserStatusEnum.active,
                UserStatusEnum.inactive
            ]
        )
        if not user:
            raise HTTPNotFound('akun pengguna tidak ditemukan')
        if user.user_status == UserStatusEnum.inactive:
            raise HTTPUnauthorized(
                'akun anda belum aktif, mohon hubungi kepala gudang')

        # Password check
        password_check = auth_service.check_password(
            payload['user_password'], user.user_password
        )
        if not password_check:
            raise HTTPUnauthorized('password anda tidak sesuai')

        # Single device check
        token = redis_repository.get(f"auth_token:{user.user_id}")

        if token:
            raise HTTPUnauthorized(
                'mohon logout terlebih dahulu akun anda di device lain'
            )

        # Login process
        environ = get_location_from_ip(
            request.environ.get('HTTP_X_REAL_IP')
        )
        environ.update(
            {
                "device": request.environ.get('HTTP_USER_AGENT')
            }
        )
        access_token = auth_service.generate_access_token(user, environ)

        redis_repository.set(
            key=f"notification_token:{user.user_id}",
            value=payload['user_notification_token'],
            expire_seconds=request.registry.settings.get(
                'auth.expiration_seconds'
            )
        )

        redis_repository.set(
            key=f"auth_token:{user.user_id}",
            value=access_token,
            expire_seconds=request.registry.settings.get(
                'auth.expiration_seconds'
            )
        )

        self.user_repository.update_user(
            user=user,
            new_data={
                'user_is_login': True
            }
        )

        return {
            "error": False,
            "message": "Login berhasil",
            "role": user.user_role,
            "role_id": None,
            "access_token": access_token
        }

    def logout_handler(
        self,
        request
    ) -> dict:
        user_id = request.user.get('user_id')
        user = self.user_repository.get_user_by_identifier(
            identifier_type='id',
            user_identifier=user_id
        )
        redis_repository = RedisRepository(request.redis_conn)

        redis_repository.delete(f"auth_token:{user_id}")
        redis_repository.delete(f"notification_token:{user_id}")

        self.user_repository.update_user(
            user=user,
            new_data={
                'user_is_login': False
            }
        )

        return {
            "error": False,
            "message": "Logout berhasil"
        }
