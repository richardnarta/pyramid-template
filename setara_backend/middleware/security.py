import jwt
from pyramid.authentication import CallbackAuthenticationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from zope.interface import implementer
from setara_backend.repositories import RedisRepository


def get_token_from_request(request):
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        return auth_header.split(' ')[1]
    return None


@implementer(IAuthenticationPolicy)
class JWTAuthenticationPolicy(CallbackAuthenticationPolicy):
    """
    A Pyramid authentication policy that authenticates users based on a JWT.
    Its only job is to identify the user and their principals (roles).
    """

    def __init__(self, secret, algorithms, token_expirations):
        self.secret = secret
        self.algorithms = algorithms
        self.expiration = token_expirations

    def unauthenticated_userid(self, request):
        token = get_token_from_request(request)
        if token is None:
            request.user = None
            return None

        try:
            auth_service = request.auth_service
            claims = auth_service.get_user_from_access_token(token)
            user_id = claims.get('user_id')

            # Check if token is still valid in Redis (not logged out)
            redis_repo = RedisRepository(request.redis_conn)
            key = f"auth_token:{user_id}"
            stored_token = redis_repo.get(key)

            if stored_token != token:
                request.user = None
                return None

            # Reset token expiration time
            redis_repo.set(key, stored_token, expire_seconds=self.expiration)

            # Add decoded token to request
            request.user = claims

            return user_id
        except jwt.PyJWTError:
            return None

    def remember(self, request, userid, **kw):  # pragma: no cover
        """
        This policy does not handle generating tokens, so we return no headers.
        Token creation happens in the login view.
        """
        return []

    def forget(self, request):  # pragma: no cover
        """
        This policy does not handle logging out. The token is simply
        removed from Redis in the logout view. We return no headers.
        """
        return []


def includeme(config):
    settings = config.get_settings()
    auth_secret = settings['auth.secret']
    auth_algorithms = settings['auth.algorithm']
    token_expirations = settings['auth.expiration_seconds']

    security_policy = JWTAuthenticationPolicy(
        auth_secret, auth_algorithms, token_expirations)
    config.set_security_policy(security_policy)
