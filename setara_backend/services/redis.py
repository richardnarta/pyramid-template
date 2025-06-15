import redis
import fakeredis


def includeme(config):
    """
    This function specifically sets up the Redis service.
    """

    settings = config.get_settings()
    is_testing = settings.get('testing', False)
    redis_instance = settings.get('redis.instance', None)

    if is_testing and redis_instance:
        config.add_request_method(
            lambda r: redis_instance, 'redis_conn', reify=True
        )
    else:  # pragma: no cover
        host = settings.get('redis.host')
        port = int(settings.get('redis.port'))
        db = int(settings.get('redis.db'))
        pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
        )
        config.registry['redis.pool'] = pool

        def get_redis_conn(request):
            return redis.Redis(connection_pool=request.registry['redis.pool'])

        config.add_request_method(get_redis_conn, 'redis_conn', reify=True)
