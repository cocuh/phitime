from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.session import SignedCookieSessionFactory

from phitime.db import (
    DBSession,
    Base,
)
from phitime.timetable.renderer import SVGTimetableRendererFactory


required_plugins = [
    'pyramid_jinja2',
]


def _load_secret_ini(settings):
    import  six.moves 

    secret_ini = settings.get("phitime.secret.ini", None)
    if secret_ini is None:
        return

    config = six.moves.configparser.ConfigParser()
    config.read([secret_ini])

    for section in settings['phitime.secret.sections'].strip().splitlines():
        settings.update(config.items(section))
    return settings

def _gen_session_factory(settings):
    return SignedCookieSessionFactory(settings['phitime.session_secret'])

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    _load_secret_ini(settings)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    
    config = Configurator(settings=settings)
    config.set_session_factory(_gen_session_factory(settings))
    config.add_renderer(name='svg_timetable', factory=SVGTimetableRendererFactory)
    for plugin_name in required_plugins:
        config.include(plugin_name)

    config.add_static_view('static/bootstrap', 'resources/bootstrap/dist', cache_max_age=3600)
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    config.add_route('top', '/')
    config.add_route('event.create', '/event_create/')
    config.add_route('event.detail', '/event/{event_scrambled_id}/')
    config.add_route('event.detail.timetable', '/event/{event_scrambled_id}/timetable.svg')
    config.add_route('event.edit', '/event/{event_scrambled_id}/edit/')
    config.add_route('event.edit.proposed', '/event/{event_scrambled_id}/edit/proposed/')
    config.add_route('event.edit.proposed.timetable', '/event/{event_scrambled_id}/edit/proposed/timetable.svg')
    config.add_route('event.api.info', '/event/{event_scrambled_id}/api/info.json')
    config.add_route('member.create', '/event/{event_scrambled_id}/create_member/')
    config.add_route('member.edit', '/event/{event_scrambled_id}/{member_position}/edit/')
    config.add_route('member.edit.timetable', '/event/{event_scrambled_id}/{member_position}/edit/timetable.svg')
    config.add_route('svg.timetable.univ_tsukuba', '/svg/timetable/univ_tsukuba.svg')
    config.add_route('svg.timetable.half_hourly', '/svg/timetable/half_hourly.svg')
    config.add_route('svg.calendar', '/svg/calendar.svg')

    config.scan()
    return config.make_wsgi_app()
