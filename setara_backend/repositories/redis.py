import json
from typing import Any, Optional


class RedisRepository:
    """
    A repository for interacting with Redis, providing common key-value operations.
    It automatically handles JSON serialization for complex data types.
    """

    def __init__(self, redis_connection):
        self.redis = redis_connection

    def set(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        try:
            if isinstance(value, (dict, list)):
                value_to_store = json.dumps(value)
            else:
                value_to_store = value

            if expire_seconds:
                self.redis.setex(
                    name=key, time=expire_seconds,
                    value=value_to_store
                )
            else:
                self.redis.set(name=key, value=value_to_store)
            return True
        except Exception as e:
            return False

    def get(self, key: str) -> Any:
        try:
            value = self.redis.get(key)
            if value is None:
                return None

            try:
                return json.loads(value.decode('utf-8'))
            except (json.JSONDecodeError, TypeError):
                return value.decode('utf-8')
        except Exception as e:
            return None

    def delete(self, key: str) -> int:
        try:
            return self.redis.delete(key)
        except Exception as e:
            return 0
