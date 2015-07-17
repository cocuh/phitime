from .univ_tsukuba import UnivTsukubaTimetable

timetable_types = [
    UnivTsukubaTimetable,
]


class TimetableUtils(object):
    DEFAULT = UnivTsukubaTimetable  # fixme

    @classmethod
    def find_by_name(cls, name):
        for timetable in timetable_types:
            if timetable.name == name:
                return timetable

    @classmethod
    def is_exist(cls, name):
        return cls.find_by_name(name) is not None

    @classmethod
    def is_default(cls, timetable_type):
        return timetable_type == cls.DEFAULT
