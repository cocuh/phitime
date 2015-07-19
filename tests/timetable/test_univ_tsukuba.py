from .. import BaseTestCase


class TestUnivTsukubaTimetable(BaseTestCase):
    def _getTargetClass(self):
        from phitime.timetable.univ_tsukuba import UnivTsukubaTimetable
        return UnivTsukubaTimetable

    def _makeOne(self, start_date=None):
        if start_date is None:
            import datetime
            start_date = datetime.date(2015, 7, 18)
        UnivTsukubaTimetable = self._getTargetClass()
        return UnivTsukubaTimetable(start_date)

    def test_to_string(self):
        timetable = self._makeOne()

        res = timetable.to_string()
        self.assertIsInstance(res, str)

    def test_get_name(self):
        timetable = self._makeOne()
        self.assertIsNotNone(timetable.get_name())

    def test_get_display_name(self):
        timetable = self._makeOne()
        self.assertIsNotNone(timetable.get_display_name())

    def test_get_route_name(self):
        timetable = self._makeOne()
        self.assertIsNotNone(timetable.get_route_name())
