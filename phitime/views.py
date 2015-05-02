from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import transaction

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
        event_name = self.request.params.get('event.name')
        event_description = self.request.params.get('event.description')
        event_timetable_type = self.request.params.get('event.timetable_type')

        with transaction.manager:
            event = Event.create(event_name, event_description, event_timetable_type)
            event.validate()
            DBSession.add(event)
    
        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='event.edit', request_method='GET', renderer='templates/event/edit.jinja2')
    def edit_get(self):
        return {
            'event': self.event,
            'TimetableType': TimetableType,
        }

    @view_config(route_name='event.edit', request_method='POST')
    def edit_post(self):
        event_name = self.request.params.get('event.name')
        event_description = self.request.params.get('event.description')
        event_timetable_type = self.request.params.get('event.timetable_type')

        with transaction.manager:
            event = self.event
            event.name = event_name
            event.description = event_description
            event.timetable_type = event_timetable_type
            event.validate()
            DBSession.add(event)

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=self.event.scrambled_id))

    @view_config(route_name='event.detail', request_method='GET', renderer='templates/event/detail.jinja2')
    def detail_get(self):
        return {
            'event': self.event,
        }

    @view_config(route_name='event.detail', request_method='POST')
    def detail_post(self):
        return {}

    @property
    def event(self):
        scrambled_id = self.request.matchdict.get('event_scrambled_id')
        return Event.find_by_scrambled_id(scrambled_id)


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