from .base import (
    SVGTimetable,
    SVGDay,
    SVGPeriod,
    TimetableType,
)

from .half_hourly import Day as Holiday

_START_TIME = 800
_END_TIME = 2300

Holiday.START_TIME = _START_TIME
Holiday.END_TIME = _END_TIME


class Period(SVGPeriod):
    pass


class WeekDay(SVGDay):
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    splitter = [
        # 1st
        (840, "lesson"),
        955,
        # 2nd
        (1010, "lesson"),
        1125,
        # 3rd
        (1215, "lesson"),
        1330,
        # 4th
        (1345, "lesson"),
        1500,
        # 5th
        (1515, "lesson"),
        1630,
        # 6th
        (1645, "lesson"),
        1800,
        1830,
        (1900, "odd"),
        (1930, "odd"),
        2000,
        2030,
        (2100, "odd"),
        (2130, "odd"),
        2200,
        2230,
    ]

    def gen_periods(self):
        def get(time):
            if isinstance(time, tuple):
                time, classes = time
                if not isinstance(classes, list):
                    classes = [classes]
                return time, classes
            else:
                return time, []

        def gen():
            for start, end in zip([self.START_TIME] + self.splitter, self.splitter + [self.END_TIME]):
                start, classes = get(start)
                end, _ = get(end)
                yield start, end, classes

        periods = []
        for start_time, end_time, classes in gen():
            period = SVGPeriod(self.day_idx, start_time, end_time, classes)
            periods.append(period)
        return periods


class _Timetable(SVGTimetable):
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    def gen_day(self, date, day_idx):
        if date.weekday() in [5, 6]:  # sat or sunday
            return Holiday(date, day_idx)
        else:
            return WeekDay(date, day_idx)


class UnivTsukubaTimetable(TimetableType):
    def __init__(self, start_date, stylesheet_urls=[], script_urls=[]):
        self.timetable = _Timetable(start_date, 7, stylesheet_urls, script_urls)

    def to_string(self):
        return self.timetable.to_string()

    @classmethod
    def get_display_name(self):
        return u'筑波大学 時間割'

    @classmethod
    def get_name(self):
        return 'univ_tsukuba'

    @classmethod
    def get_route_name(self):
        return 'svg.timetable.univ_tsukuba'


__all__ = ['UnivTsukubaTimetable']
