from pyramid.httpexceptions import HTTPTooManyRequests
from ..repositories import RedisRepository


def rate_limiter_tween_factory(handler, registry):
    """
    Factory for the rate-limiting tween.
    """
    requests_per_second = 10
    window_seconds = 1

    def rate_limiter_tween(request):
        """
        This tween checks if a client has exceeded the request limit.
        """
        # Don't rate-limit pre-flight OPTIONS requests
        if request.method == 'OPTIONS':
            return handler(request)

        # Use the client's IP address as the identifier
        ip = request.environ.get('REMOTE_ADDR') or '127.0.0.1'
        key = f"rate_limit:{ip}"

        redis_repo = RedisRepository(request.redis_conn)

        # Use a pipeline for atomic operations
        pipeline = redis_repo.redis.pipeline()
        pipeline.incr(key)
        pipeline.expire(key, window_seconds)
        request_count, _ = pipeline.execute()

        if request_count > requests_per_second:
            raise HTTPTooManyRequests(
                json_body={
                    "error": True,
                    "message": "Rate limit exceeded"
                }
            )

        return handler(request)

    return rate_limiter_tween
