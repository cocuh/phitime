from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from phitime.db import (
    DBSession,
    Base,
)


required_plugins = [
    'pyramid_jinja2',
]


def _load_secret_ini(settings):
    import six.moves

    secret_ini = settings.get("phitime.secret_ini", None)
    if secret_ini is None:
        return

    config = six.moves.configparser.ConfigParser()
    config.read([secret_ini])

    for section in settings['phitime.secret.sections'].strip().splitlines():
        settings.update(config.items(section))
    return settings


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
    
    config.add_route('top', '/')
    config.add_route('event.create', '/event_create')
    config.add_route('event.detail', '/event/{scrambled_event_id}/')
    config.add_route('event.edit', '/event/{scrambled_event_id}/edit')
    config.add_route('member.edit', '/event/{scrambled_event_id}/{member_position}/edit')

    config.scan()
    return config.make_wsgi_app()
