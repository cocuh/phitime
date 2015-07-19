from .base import (
    SVGTimetable,
    SVGDay,
    SVGPeriod,
    TimetableType,
)

_START_TIME = 800
_END_TIME = 2300


class Day(SVGDay):
    START_TIME = _START_TIME
    END_TIME = _END_TIME
    splitter = [
        830,
        900,
        930,
        1000,
        1030,
        1100,
        1130,
        1200,
        1230,
        1300,
        1330,
        1400,
        1430,
        1500,
        1530,
        1600,
        1630,
        1700,
        1730,
        1800,
        1830,
        1900,
        1930,
        2000,
        2030,
        2100,
        2130,
        2200,
        2230,
    ]

    def gen_periods(self):
        periods = []
        for start, end in zip([self.START_TIME] + self.splitter, self.splitter + [self.END_TIME]):
            classes = []
            if start // 100 % 2 == 1:
                classes.append('odd')
            elif start // 100 % 2 == 0:
                classes.append('even')
            periods.append(SVGPeriod(self.day_idx, start, end, classes))
        return periods


class _Timetable(SVGTimetable):
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    def gen_day(self, date, day_idx):
        return Day(date, day_idx)


class HalfHourlyTimetable(TimetableType):
    def get_target_class(cls):
        return _Timetable

    def to_string(self):
        return self.timetable.to_string()

    @classmethod
    def get_name(cls):
        return 'half_hourly'

    @classmethod
    def get_display_name(cls):
        return '30分区切り'

    @classmethod
    def get_route_name(cls):
        return 'svg.timetable.half_hourly'


__all__ = ['HalfHourlyTimetable']
