from pyramid.testing import DummyRequest
from . import BaseTestCase
import transaction
from phitime.models import Event


class BaseViewTestCase(BaseTestCase):
    def setUp(self):
        super(BaseViewTestCase, self).setUp()
        self._init_route()

    def _init_route(self):
        self.config.add_route('top', '/')
        self.config.add_route('event.create', '/event_create')
        self.config.add_route('event.detail', '/event/{event_scrambled_id}/')
        self.config.add_route('event.edit', '/event/{event_scrambled_id}/edit')
        self.config.add_route('member.edit', '/event/{event_scrambled_id}/{member_position}/edit')
        self.config.add_route('timetable.univ_tsukuba', '/timetable/univ_tsukuba.svg')
        self.config.add_route('timetable.half_hourly', '/timetable/half_hourly.svg')

    def _make_event(self, name=u'いべんとなめ', description='ですくりぷしょん', timetable_type='half_hourly'):
        event = Event(name, description, timetable_type)
        self.DBSession.add(event)
        self.DBSession.flush()
        return event


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