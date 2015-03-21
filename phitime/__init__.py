from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from phitime.db import (
    DBSession,
    Base,
)


required_plugins = [
    'pyramid_chameleon',
]


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)

    for plugin_name in required_plugins:
        config.include(plugin_name)

    config.add_static_view('static/bootstrap', 'resources/bootstrap/dist', cache_max_age=3600)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
