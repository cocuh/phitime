from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from phitime.db import DBSession
from phitime.exceptions import MemberNotFoundException, EventNotFoundException
from phitime.models import Event, Member
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

        event = Event.create(event_name, event_description, event_timetable_type)
        event.validate()

        DBSession.add(event)
        DBSession.flush()

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='event.edit', request_method='GET', renderer='templates/event/edit.jinja2')
    def edit_get(self):
        return {
            'event': self.get_event(),
            'TimetableType': TimetableType,
        }

    @view_config(route_name='event.edit', request_method='POST')
    def edit_post(self):
        event_name = self.request.params.get('event.name')
        event_description = self.request.params.get('event.description')
        event_timetable_type = self.request.params.get('event.timetable_type')

        event = self.get_event()
        event.name = event_name
        event.description = event_description
        event.timetable_type = event_timetable_type
        event.validate()

        DBSession.add(event)
        DBSession.flush()

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=self.get_event().scrambled_id))

    @view_config(route_name='event.detail', request_method='GET', renderer='templates/event/detail.jinja2')
    def detail_get(self):
        return {
            'event': self.get_event(),
        }

    @view_config(route_name='event.detail', request_method='POST')
    def detail_post(self):
        return {}

    def get_event(self):
        scrambled_id = self.request.matchdict.get('event_scrambled_id')
        return Event.find_by_scrambled_id(scrambled_id)


class MemberView(object):
    def __init__(self, request):
        self.request = request

    @view_config(route_name='member.create', request_method='GET', renderer='templates/member/create.jinja2')
    def create_get(self):
        return {
            'event': self.get_event(),
            'member': self.get_member(),
            'TimetableType': TimetableType,
        }

    @view_config(route_name='member.create', request_method='POST')
    def create_post(self):
        member_name = self.request.params.get('member.name')
        member_comment = self.request.params.get('member.comment')

        event = self.get_event()

        member = event.create_member(member_name, member_comment)
        member.validate()

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='member.edit', request_method='GET', renderer='templates/member/edit.jinja2')
    def edit_get(self):
        return {
            'event': self.get_event(),
            'member': self.get_member(),
            'TimetableType': TimetableType,
        }

    @view_config(route_name='member.edit', request_method='POST')
    def edit_post(self):
        member_name = self.request.params.get('member.name')
        member_comment = self.request.params.get('member.comment')

        event = self.get_event()
        member = self.get_member()

        member.name = member_name
        member.comment = member_comment

        member.validate()

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    def get_event(self):
        scrambled_id = self.request.matchdict.get('event_scrambled_id')
        if scrambled_id is None:
            raise EventNotFoundException('scrambled_id is None')

        event = Event.find_by_scrambled_id(scrambled_id)

        if event is None:
            raise EventNotFoundException('scrambled_id:{}'.format(scrambled_id))
        return event

    def get_member(self):
        event = self.get_event()
        position = self.request.matchdict.get('member_position')

        if position is None:
            raise MemberNotFoundException('position is None'.format(position))

        member = Member.find(event, position).first()

        if member is None:
            raise MemberNotFoundException('event:{!r} position:{!r}'.format(
                event, position
            ))
        return member


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