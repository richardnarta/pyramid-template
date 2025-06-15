from pyramid.config import Configurator
import os


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    with Configurator(settings=settings) as config:
        config.include('.middleware')

        config.pyramid_openapi3_spec_directory(
            os.path.join(os.path.dirname(__file__), "api_docs/openapi.yaml"),
            route='/api/spec'
        )
        config.pyramid_openapi3_add_explorer()

        config.include('.services')
        config.include('.routes')
        config.scan()
    return config.make_wsgi_app()
