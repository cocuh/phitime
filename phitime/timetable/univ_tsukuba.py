from .base import (
    SVGTimetable,
    SVGDay,
    SVGPeriod,
    TimetableType,
)

_START_TIME = 800
_END_TIME = 2300


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


class Holiday(SVGDay):
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
            WeekDay(start_date),
            WeekDay(start_date),
            WeekDay(start_date),
            WeekDay(start_date),
            WeekDay(start_date),
            Holiday(start_date),
            Holiday(start_date),
        ]


class UnivTsukubaTimetable(TimetableType):
    name = 'univ_tsukuba'
    def __init__(self, start_date):
        self.timetable = _Timetable(start_date)

    def to_string(self):
        return self.timetable.to_string()


__all__ = ['UnivTsukubaTimetable']
