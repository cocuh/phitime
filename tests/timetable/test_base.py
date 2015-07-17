from unittest.mock import Mock

from .. import BaseTestCase


class TestSvtTimetable(BaseTestCase):
    def _getTargetClass(self):
        """
        :rtype: phitime.timetable.base.SVGTimetable
        """
        from phitime.timetable.base import SVGTimetable
        return SVGTimetable

    def _makeOne(self, start_date=None, gen_days=None):
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
        SVGTimetable.gen_days = gen_days
        return SVGTimetable(start_date)

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
