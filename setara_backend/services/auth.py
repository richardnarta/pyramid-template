import jwt
import bcrypt
from datetime import datetime, UTC
from setara_backend.utils import UserMapper
from setara_backend.models import TblUser


class AuthService:
    """
    A service class to handle all authentication-related business logic
    """

    def __init__(self, settings):
        self.secret = settings['auth.secret']
        self.algorithm = settings['auth.algorithm']

    def hash_password(self, plain_text_password: str) -> str:
        """Hashes a password using bcrypt."""
        password_bytes = plain_text_password.encode('utf-8')
        hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    def check_password(self, plain_text_password: str, hashed_password: str) -> bool:
        """Checks a plain-text password against a stored bcrypt hash."""
        password_bytes = plain_text_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)

    def generate_access_token(self, user: TblUser, payload: dict) -> str:
        """Generates a JWT access token."""
        payload.update(UserMapper.db_to_access_token(user))
        payload.update({'iat': datetime.now(UTC)})
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    def get_user_from_access_token(self, access_token):
        """Decode a JWT access token to user dict"""
        return jwt.decode(access_token, self.secret, algorithms=[self.algorithm])
