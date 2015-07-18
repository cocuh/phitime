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
        return [
            SVGPeriod(self.day_idx, start_time, end_time)
            for start_time, end_time
            in zip([self.START_TIME] + self.splitter, self.splitter + [self.END_TIME])
            ]


class _Timetable(SVGTimetable):
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    def gen_days(self, start_date):
        # TODO user start_date
        return [
            Day(start_date),
            Day(start_date),
            Day(start_date),
            Day(start_date),
            Day(start_date),
            Day(start_date),
            Day(start_date),
        ]


class HalfHourlyTimetable(TimetableType):
    name = 'half_hourly'

    def __init__(self, start_date):
        self.timetable = _Timetable(start_date)

    def to_string(self):
        return self.timetable.to_string()


__all__ = ['HalfHourlyTimetable']
