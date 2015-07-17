from pyramid.testing import DummyRequest
from phitime.models import Event

from . import BaseTestCase

class BaseViewTestCase(BaseTestCase):
    def setUp(self):
        super(BaseViewTestCase, self).setUp()
        self._init_route()

    def _init_route(self):
        config = self.config
        config.add_route('top', '/')
        config.add_route('event.create', '/event_create')
        config.add_route('event.detail', '/event/{event_scrambled_id}/')
        config.add_route('event.edit', '/event/{event_scrambled_id}/edit')
        config.add_route('member.create', '/event/{event_scrambled_id}/create_member')
        config.add_route('member.edit', '/event/{event_scrambled_id}/{member_position}/edit')
        config.add_route('timetable.univ_tsukuba', '/timetable/univ_tsukuba.svg')
        config.add_route('timetable.half_hourly', '/timetable/half_hourly.svg')

    def _make_event(self, name=u'いべんとなめ', description=u'ですくりぷしょん', timetable_type='half_hourly'):
        event = Event(name, description, timetable_type)
        self.DBSession.add(event)
        self.DBSession.flush()
        return event

    def _make_member(self, event, name=u'めんばーなめ', comment=u'めんばーこまんと'):
        member = event.create_member(name, comment)
        self.DBSession.add(member)
        self.DBSession.flush()
        return member


class ViewEventCreatePostTests(BaseViewTestCase):
    def _callFUT(self, request):
        from phitime.views import EventView

        return EventView(request).create_post()

    def test_it(self):
        from phitime.models import Event

        event_name = 'いべんとだよ'
        event_description = 'せつめいぶんだよ'
        event_timetable_type = 'half_hourly'

        self.assertEqual(Event.query.count(), 0)
        request = DummyRequest({
            'event.name': event_name,
            'event.description': event_description,
            'event.timetable_type': event_timetable_type,
        })

        response = self._callFUT(request)

        self.assertEqual(Event.query.count(), 1)
        event = Event.query.first()
        self.assertEqual(event.name, event_name)
        self.assertEqual(event.description, event_description)
        self.assertEqual(event.timetable_type.name, event_timetable_type)

        self.assertEqual(response.location, request.route_path('event.detail', event_scrambled_id=event.scrambled_id))

    def test_no_name(self):
        from phitime.exceptions import ValidationException

        request = DummyRequest({
            'event.description': '',
            'event.timetable_type': '',
        })

        self.assertRaises(ValidationException, self._callFUT, request)

    def test_no_description(self):
        from phitime.exceptions import ValidationException

        request = DummyRequest({
            'event.name': '',
            'event.timetable_type': '',
        })

        self.assertRaises(ValidationException, self._callFUT, request)

    def test_no_timetable_type(self):
        from phitime.exceptions import ValidationException

        request = DummyRequest({
            'event.name': '',
            'event.description': '',
        })

        self.assertRaises(ValidationException, self._callFUT, request)

    def test_no_exist_timetable_type(self):
        from phitime.exceptions import ValidationException

        request = DummyRequest({
            'event.name': '',
            'event.description': '',
            'event.timetable_type': 'NO_SUCH_TIMETABLE_TYPE',
        })

        self.assertRaises(ValidationException, self._callFUT, request)


class ViewEventEditPostTests(BaseViewTestCase):
    def _callFUT(self, request):
        from phitime.views import EventView

        return EventView(request).edit_post()

    def test_it(self):
        event = self._make_event()

        event_name = 'event name'
        event_description = 'event description'
        event_timetable_type = 'half_hourly'

        request = DummyRequest({
            'event.name': event_name,
            'event.description': event_description,
            'event.timetable_type': event_timetable_type
        })

        request.matchdict['event_scrambled_id'] = event.scrambled_id

        response = self._callFUT(request)

        self.assertEqual(event.name, event_name)
        self.assertEqual(event.description, event_description)
        self.assertEqual(event.timetable_type.name, event_timetable_type)
        self.assertEqual(response.location, request.route_path('event.detail', event_scrambled_id=event.scrambled_id))


class ViewMemberCreatePostTests(BaseViewTestCase):
    def _callFUT(self, request):
        from phitime.views import MemberView

        return MemberView(request).create_post()

    def test_it(self):
        event = self._make_event()

        member_name = 'member name'
        member_comment = 'member comment'

        request = DummyRequest({
            'member.name': member_name,
            'member.comment': member_comment,
        })
        request.matchdict['event_scrambled_id'] = event.scrambled_id

        self.assertEqual(event.last_member_position, 0)

        response = self._callFUT(request)

        from phitime.models import Member

        member = Member.query.first()
        self.assertEqual(response.location, request.route_path('event.detail', event_scrambled_id=event.scrambled_id))
        self.assertEqual(member.name, member_name)
        self.assertEqual(member.comment, member_comment)
        self.assertEqual(event.last_member_position, 1)


class ViewMemberEditPostTests(BaseViewTestCase):
    def _callFUT(self, request):
        from phitime.views import MemberView

        return MemberView(request).edit_post()

    def test_it(self):
        event = self._make_event()
        member = self._make_member(event)

        member_name = 'member name'
        member_comment = 'member comment'

        request = DummyRequest({
            'member.name': member_name,
            'member.comment': member_comment,
        })
        request.matchdict['event_scrambled_id'] = event.scrambled_id
        request.matchdict['member_position'] = member.position

        self.assertEqual(event.last_member_position, 1)

        response = self._callFUT(request)

        from phitime.models import Member

        member = Member.query.first()
        self.assertEqual(response.location, request.route_path('event.detail', event_scrambled_id=event.scrambled_id))
        self.assertEqual(member.name, member_name)
        self.assertEqual(member.comment, member_comment)
        self.assertEqual(event.last_member_position, 1)

