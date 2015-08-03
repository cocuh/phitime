from unittest.mock import Mock

from .. import BaseTestCase


class TestSvgTimetable(BaseTestCase):
    def _getTargetClass(self):
        """
        :rtype: phitime.timetable.base.SVGTimetable
        """
        from phitime.timetable.base import SVGTimetable
        return SVGTimetable

    def _makeOne(self, start_date=None, day_length=7,
            gen_days=None, stylesheet_urls=[], script_urls=[],
            start_time=800, end_time=2300):
        """
        :rtype: phitime.timetable.base.SVGTimetable
        """
        SVGTimetable = self._getTargetClass()
        if start_date is None:
            import datetime
            start_date = datetime.date(1995, 2, 14)
        if gen_days is None:
            gen_days = Mock()
            gen_days.return_value = []
        SVGTimetable.START_HHMM = start_time
        SVGTimetable.END_HHMM = end_time
        SVGTimetable._gen_days = gen_days
        SVGTimetable.__abstractmethods__ = {}
        return SVGTimetable(start_date, day_length, stylesheet_urls, script_urls)

    def test_create(self):
        import datetime
        start_date = datetime.date(1995, 2, 14)

        timetable = self._makeOne(start_date)

        self.assertEqual(timetable.start_date, start_date)
        self.assertEqual(timetable.days, [])

    def test_to_elem(self):
        timetable = self._makeOne()
        from xml.etree.ElementTree import Element

        self.assertIsInstance(timetable.to_elem(), Element)

    def test_to_string(self):
        timetable = self._makeOne()

        self.assertIsInstance(timetable.to_string(), str)
        self.assertTrue(timetable.to_string().startswith('<svg '))


class TestSVGDay(BaseTestCase):
    def _getTargetClass(self):
        from phitime.timetable.base import SVGDay
        return SVGDay

    def _makeOne(self, date=None, day_idx=0, gen_periods=None):
        """
        :rtype: phitime.timetable.base.SVGDay
        """
        SVGDay = self._getTargetClass()
        if date is None:
            import datetime
            date = datetime.date(1995, 2, 14)
        if gen_periods is None:
            gen_periods = Mock()
            gen_periods.return_value = []
        SVGDay.gen_periods = gen_periods
        SVGDay.__abstractmethods__ = {}
        return SVGDay(date, day_idx)

    def test_create(self):
        import datetime
        date = datetime.date(1995, 2, 14)

        day = self._makeOne(date)

        self.assertEqual(day.date, date)

    def test_to_elem(self):
        from phitime.timetable.base import SVGPeriod
        import datetime
        date = datetime.date(1995, 2, 14)

        gen_periods = Mock()
        gen_periods.return_value = [
            SVGPeriod(date, 0, 800, 900),
            SVGPeriod(date, 0, 900, 1300),
            SVGPeriod(date, 0, 1300, 2300),
        ]

        day = self._makeOne(gen_periods=gen_periods)

        from xml.etree.ElementTree import Element

        elem = day.to_elem()

        self.assertIsInstance(elem, Element)
        self.assertEqual(len(elem), len(gen_periods.return_value) + 1)  # +1 for header


class TestSVGPeriod(BaseTestCase):
    def _getTargetClass(self):
        from phitime.timetable.base import SVGPeriod
        return SVGPeriod

    def _makeOne(self, day_idx=1, start_time=800, end_time=2300, classes=[]):
        SVGPeriod = self._getTargetClass()
        return SVGPeriod(
            day_idx=day_idx,
            start_time=start_time,
            end_time=end_time,
            classes=classes
        )
