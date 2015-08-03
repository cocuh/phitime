from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from phitime.db import DBSession
from phitime.exceptions import MemberNotFoundException, EventNotFoundException
from phitime.model_helper import MemberHelper, EventHelper
from phitime.models import Event, Member
from phitime.timetable import TimetableUtils
from phitime.timetable.strategy import ClassStrategies as TimetableClassesStrategies


class BaseView(object):
    def __init__(self, request):
        self.request = request


class TopView(BaseView):
    @view_config(route_name='top', renderer='templates/top.jinja2')
    def top(self):
        return {
            'Event': Event,
        }


class UserView(BaseView):
    pass


class EventView(BaseView):
    @view_config(route_name='event.create', request_method='GET', renderer='templates/event/create.jinja2')
    def create_get(self):
        return {
            'TimetableUtils': TimetableUtils,
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

        return HTTPFound(self.request.route_path('event.edit.proposed', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='event.edit', request_method='GET', renderer='templates/event/edit.jinja2')
    def edit_get(self):
        return {
            'event': self.get_event(),
            'TimetableUtils': TimetableUtils,
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

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='event.edit.proposed', request_method='GET',
        renderer='templates/event/edit_proposed_time.jinja2')
    def edit_proposed_time_get(self):
        event = self.get_event()
        return {
            'event': event,
        }

    @view_config(route_name='event.edit.proposed', request_method='POST')
    def edit_proposed_time_post(self):
        event = self.get_event()
        proposed_times_json_str = self.request.params.get('event.proposed_times')

        event.clear_proposed_times()
        proposed_times = EventHelper.gen_proposed_times(event, proposed_times_json_str)
        DBSession.add_all(proposed_times)

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='event.edit.proposed.timetable', request_method='GET', renderer='svg_timetable')
    def edit_proposed_timetable(self):
        event = self.get_event()
        return {
            'page': 0,
            'is_editable': True,
            'event': event,
            'class_strategies': [
                TimetableClassesStrategies.is_the_event_proposed,
            ],
        }

    @view_config(route_name='event.detail', request_method='GET', renderer='templates/event/detail.jinja2')
    def detail_get(self):
        return {
            'event': self.get_event(),
        }

    @view_config(route_name='event.detail', request_method='POST')
    def detail_post(self):
        return {}

    @view_config(route_name='event.detail.timetable', request_method='GET', renderer='svg_timetable')
    def edit_proposed_timetable(self):
        event = self.get_event()
        return {
            'page': 0,
            'is_editable': False,
            'event': event,
            'class_strategies': [
                TimetableClassesStrategies.is_unavailable,
                TimetableClassesStrategies.available_member,
            ],
        }

    @view_config(route_name='event.api.info', renderer='json')
    def info(self):
        return {
            'event': self.get_event(),
        }

    def get_event(self):
        scrambled_id = self.request.matchdict.get('event_scrambled_id')
        return Event.find_by_scrambled_id(scrambled_id)


class MemberView(BaseView):
    @view_config(route_name='member.create', request_method='GET', renderer='templates/member/create.jinja2')
    def create_get(self):
        return {
            'event': self.get_event(),
            'TimetableUtils': TimetableUtils,
        }

    @view_config(route_name='member.create', request_method='POST')
    def create_post(self):
        member_name = self.request.params.get('member.name')
        member_comment = self.request.params.get('member.comment')
        available_times = []  # TODO

        event = self.get_event()

        member = event.create_member(member_name, member_comment, available_times)
        member.validate()

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='member.edit', request_method='GET', renderer='templates/member/edit.jinja2')
    def edit_get(self):
        return {
            'event': self.get_event(),
            'member': self.get_member(),
            'TimetableUtils': TimetableUtils,
        }

    @view_config(route_name='member.edit', request_method='POST')
    def edit_post(self):
        member_name = self.request.params.get('member.name')
        member_comment = self.request.params.get('member.comment')
        available_times_json = self.request.params.get('member.available_times')

        event = self.get_event()
        member = self.get_member()
        member.clear_available_times()

        available_times = MemberHelper.gen_available_times(event, member, available_times_json)

        member.name = member_name
        member.comment = member_comment

        DBSession.add_all(available_times)

        member.validate()

        return HTTPFound(self.request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    @view_config(route_name='member.edit.timetable', renderer='svg_timetable')
    def edit_timetable(self):
        event = self.get_event()
        member = self.get_member()
        return {
            'event': event,
            'member': member,
            'class_strategies': [
                TimetableClassesStrategies.is_the_member_available,
                TimetableClassesStrategies.is_unavailable,
            ],
            'is_editable': True,
        }

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


class SVGView(BaseView):
    CONTENT_TYPE_SVG = 'image/svg+xml'

    @view_config(route_name='svg.timetable.univ_tsukuba', http_cache=3600, renderer='svg_timetable')
    def timetable_univ_tsukuba(self):
        import datetime
        UnivTsukubaTimetable = TimetableUtils.find_by_name('univ_tsukuba')
        timetable = UnivTsukubaTimetable(
            datetime.datetime.today(),
            [self.request.static_path("phitime:static/timetables/univ_tsukuba_timetable.css")],
            [self.request.static_path("phitime:static/timetables/timetable.js")]
        )
        return {
            'timetable': timetable,
        }

    @view_config(route_name='svg.timetable.half_hourly', http_cache=3600, renderer='svg_timetable')
    def timetable_half_hourly(self):
        import datetime
        HalfHourlyTimetable = TimetableUtils.find_by_name('half_hourly')
        timetable = HalfHourlyTimetable(
            datetime.datetime.today(),
            [self.request.static_path("phitime:static/timetables/univ_tsukuba_timetable.css")],
            [self.request.static_path("phitime:static/timetables/timetable.js")]
        )
        return {
            'timetable': timetable,
        }

    @view_config(route_name='svg.calendar', renderer='templates/svg/calendar/calendar.jinja2',
        http_cache=3600)
    def calendar(request):
        return {
            "week_num": 5,
        }
