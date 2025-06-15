import pytest
import fakeredis
from sqlalchemy import create_engine
from webtest import TestApp
from setara_backend import main
from setara_backend.models.meta import Base
from sqlalchemy.orm import sessionmaker
import transaction


@pytest.fixture(scope='session')
def test_redis_instance():
    """
    Creates and returns a single, session-scoped fakeredis instance.
    This ensures that all tests in the session use the same redis server instance,
    which is efficient.
    """
    fake_redis_server = fakeredis.FakeStrictRedis()
    return fake_redis_server


@pytest.fixture(scope='session')
def test_db_engine():
    """Create a new in-memory SQLite database engine for the test session."""
    # Using a fast, in-memory SQLite database for tests
    engine = create_engine('sqlite:///:memory:')
    # Create all tables defined in models
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope='session')
def TestSessionFactory(test_db_engine):
    """Returns a session factory bound to the test database engine."""
    return sessionmaker(bind=test_db_engine)


@pytest.fixture(scope='session')
def testapp(test_redis_instance, test_db_engine):
    """
    This fixture calls your main() function to create a testable
    instance of your Pyramid application.
    """
    test_settings = {
        'testing': True,
        'pyramid.includes': 'pyramid_openapi3',
        'auth.secret': 'secret',
        'auth.algorithm': 'HS256',
        'auth.expiration_seconds': '60',
        'db.engine': test_db_engine,
        'redis.instance': test_redis_instance,
    }

    app = main({}, **test_settings)

    # Wrap the app in WebTest's TestApp for sending fake requests
    return TestApp(app)


# DB session

@pytest.fixture
def dbsession(TestSessionFactory, test_db_engine):
    """
    Provides a database session for a test and guarantees a clean slate
    by DELETING all data from all tables after the test completes.

    This method provides absolute test isolation.
    """
    session = TestSessionFactory()

    # Yield the session to the test
    yield session

    # --- Teardown Phase (after the test is done) ---
    with test_db_engine.connect() as connection:
        # We need a transaction to wrap our deletions
        trans = connection.begin()

        # Go through all tables in reverse dependency order and delete from them
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())

        # Commit the deletions
        trans.commit()


# Redis client

@pytest.fixture
def redis_client(test_redis_instance):
    """
    Provides a Redis session for a single test.
    This fixture takes the session-scoped redis instance and yields it to the test.
    After the test function completes, it flushes the database to ensure
    that each test runs in isolation with a clean state.
    """
    # Yield the fake redis instance for the test to use.
    yield test_redis_instance

    # Teardown: After the test is finished, clear all keys in the database.
    test_redis_instance.flushdb()
