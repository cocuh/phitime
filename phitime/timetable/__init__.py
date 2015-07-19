from .univ_tsukuba import UnivTsukubaTimetable
from .half_hourly import HalfHourlyTimetable


class TimetableUtils(object):
    DEFAULT = HalfHourlyTimetable

    timetable_types = [
        UnivTsukubaTimetable,
        HalfHourlyTimetable,
    ]

    @classmethod
    def find_by_name(cls, name):
        for timetable in cls.timetable_types:
            if timetable.get_name() == name:
                return timetable

    @classmethod
    def is_exist(cls, name):
        return cls.find_by_name(name) is not None

    @classmethod
    def is_default(cls, timetable_type):
        return timetable_type == cls.DEFAULT


__all__ = ['TimetableUtils']
