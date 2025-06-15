import pytest
from setara_backend.repositories.redis import RedisRepository


@pytest.fixture
def redis_repo(redis_client) -> RedisRepository:
    """
    A fixture that creates an instance of RedisRepository for each test,
    injecting the clean redis_client.
    """
    return RedisRepository(redis_client)


class TestRedisRepository:
    """A test suite for the RedisRepository class."""

    def test_set_and_get_simple_string(self, redis_repo: RedisRepository):
        # Setup
        key = "test:string"
        value = "hello world"
        set_result = redis_repo.set(key, value)

        # Action
        retrieved_value = redis_repo.get(key)

        # Assert
        assert set_result is True
        assert retrieved_value == value
        assert isinstance(retrieved_value, str)

    def test_set_and_get_dict_value(self, redis_repo: RedisRepository):
        """
        Tests that a dictionary is correctly serialized to JSON, stored,
        and deserialized upon retrieval.
        """
        # Setup
        key = "test:dict"
        value = {"name": "John Doe", "age": 30, "active": True}
        set_result = redis_repo.set(key, value)

        # Action
        retrieved_value = redis_repo.get(key)

        # Assert
        assert set_result is True
        assert retrieved_value == value
        assert isinstance(retrieved_value, dict)

    def test_set_and_get_list_value(self, redis_repo: RedisRepository):
        """
        Tests that a list is correctly serialized to JSON, stored,
        and deserialized upon retrieval.
        """
        # Setup
        key = "test:list"
        value = [1, "test", None, True]
        set_result = redis_repo.set(key, value)

        # Action
        retrieved_value = redis_repo.get(key)

        # Assert
        assert set_result is True
        assert retrieved_value == value
        assert isinstance(retrieved_value, list)

    def test_get_non_existent_key(self, redis_repo: RedisRepository):
        """
        Tests that getting a key that does not exist returns None.
        """
        # Action
        retrieved_value = redis_repo.get("does:not:exist")

        # Assert
        assert retrieved_value is None

    def test_set_with_expiration(self, redis_repo: RedisRepository, redis_client):
        """
        Tests that a key can be set with an expiration time (TTL).
        """
        # Setup
        key = "test:ttl"
        value = "this will expire"
        expire_seconds = 60
        redis_repo.set(key, value, expire_seconds=expire_seconds)

        # Action and Assert
        ttl = redis_client.ttl(key)
        assert ttl > 0
        assert ttl <= expire_seconds

    def test_delete_existing_key(self, redis_repo: RedisRepository):
        """
        Tests that deleting an existing key works as expected.
        """
        # Setup
        key = "test:to:delete"
        value = "some data"
        redis_repo.set(key, value)
        assert redis_repo.get(key) == value

        # Action
        delete_result = redis_repo.delete(key)

        # Assert
        assert delete_result == 1
        assert redis_repo.get(key) is None

    def test_delete_non_existent_key(self, redis_repo: RedisRepository):
        """
        Tests that attempting to delete a non-existent key returns 0.
        """
        # Setup
        key = "already:gone"

        # Action
        delete_result = redis_repo.delete(key)

        # Assert
        assert delete_result == 0

    def test_set_failure_returns_false(self, redis_repo: RedisRepository, mocker):
        """
        Tests that the set method returns False if the underlying client fails.
        """
        # Setup
        mocker.patch.object(
            redis_repo.redis, 'set',
            side_effect=Exception("Connection failed")
        )

        # Action
        set_result = redis_repo.set("any:key", "any:value")

        # Assert
        assert set_result is False

    def test_get_failure_returns_none(self, redis_repo: RedisRepository, mocker):
        """
        Tests that the get method returns None if the underlying client fails.
        """
        # Setup
        mocker.patch.object(
            redis_repo.redis, 'get',
            side_effect=Exception("Connection failed")
        )

        # Action
        retrieved_value = redis_repo.get("any:key")

        # Assert
        assert retrieved_value is None

    def test_delete_failure_returns_zero(self, redis_repo: RedisRepository, mocker):
        """
        Tests that the delete method returns 0 if the underlying client fails.
        """
        # Setup
        mocker.patch.object(
            redis_repo.redis, 'delete',
            side_effect=Exception("Connection failed")
        )

        # Action
        delete_result = redis_repo.delete("any:key")

        # Assert
        assert delete_result == 0
