from pyramid.testing import DummyRequest
from . import BaseTestCase


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


class ViewEventCreatePostTests(BaseViewTestCase):
    def _callFUT(self, request):
        from phitime.views import EventView

        return EventView(request).create_post()

    def test_it(self):
        request = DummyRequest({
            'event.name': 'いべんとだよ',
            'event.description': 'せつめいぶんだよ',
            'event.timetable_type': 'half_hourly',
        })
        req = self._callFUT(request)
        print(req)