from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from phitime.db import DBSession
from phitime.models import Event
from phitime.timetable import TimetableType


class TopView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='top', renderer='templates/top.jinja2')
    def top(self):
        return {}


class UserView(object):
    def __init__(self, request):
        self.request = request


class EventView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='event.create', request_method='GET', renderer='templates/event/create.jinja2')
    def create_get(self):
        return {
            'TimetableType': TimetableType,
        }

    @view_config(route_name='event.create', request_method='POST', check_csrf=True)
    def create_post(self):
        event_name = self.request.params.get('event_name')
        event_description = self.request.params.get('event_description')
        timetable_type = self.request.params.get('timetable_type')
        event = Event.create(event_name, event_description, timetable_type)
        DBSession.add(event)
        return HTTPFound(self.request.route_path('event.detail'))

    @view_config(route_name='event.edit', request_method='GET', renderer='templates/event/edit.jinja2')
    def edit_get(self):
        pass

    @view_config(route_name='event.edit', request_method='POST')
    def edit_post(self):
        pass

    @view_config(route_name='event.detail', request_method='GET', renderer='tempaltes/event/detail.jinja2')
    def detail_get(self):
        pass

    @view_config(route_name='event.detail', request_method='POST')
    def detail_post(self):
        pass


class MemberView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='member.edit', request_method='GET', renderer='templates/member/edit.jinja2')
    def edit_get(self):
        pass

    @view_config(route_name='member.edit', request_method='POST')
    def edit_post(self):
        pass


class TimetableView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='timetable.univ_tsukuba', renderer='templates/timetable/univ_tsukuba.jinja2',
        http_cache=3600)
    def univ_tsukuba(self):
        self.request.response.content_type = 'image/svg+xml'
        return {}

    @view_config(route_name='timetable.half_hourly', renderer='templates/timetable/half_hourly.jinja2',
        http_cache=3600)
    def univ_tsukuba(self):
        self.request.response.content_type = 'image/svg+xml'
        return {}