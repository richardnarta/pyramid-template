from .auth import AuthService


def includeme(config):
    """
    This master 'includeme' orchestrates the setup of all services.
    """
    # Include the database service
    config.include('.database')

    # Include the redis service
    config.include('.redis')

    # Include Auth Service in request
    auth_service = AuthService(config.get_settings())
    config.add_request_method(
        lambda r: auth_service, 'auth_service', reify=True
    )
