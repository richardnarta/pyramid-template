from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker, configure_mappers
import zope.sqlalchemy


def get_engine(settings, prefix='sqlalchemy.'):
    engine = settings.get('db.engine')
    if engine:
        return engine

    return engine_from_config(settings, prefix)  # pragma: no cover


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def get_tm_session(session_factory, transaction_manager):
    dbsession = session_factory()
    zope.sqlalchemy.register(
        dbsession, transaction_manager=transaction_manager)
    return dbsession


def includeme(config):
    """
    This function sets up the database service, including transaction management.
    """

    settings = config.get_settings()

    settings['tm.manager_hook'] = 'pyramid_tm.explicit_manager'

    # Use pyramid_tm to hook the transaction lifecycle to the request
    config.include('pyramid_tm')

    # Use pyramid_retry to retry a request when transient exceptions occur
    config.include('pyramid_retry')

    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        'dbsession',
        reify=True
    )

    configure_mappers()
