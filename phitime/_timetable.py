class TimetableType(object):
    """manage all TimetableType.
    """

    timetable_types = []
    """:type: list[TimetableType]"""
    default_type = None
    """:type: TimetableType"""

    def __init__(self, name, route_name, display_name):
        self.name = name
        self.display_name = display_name
        self.route_name = route_name

    def __repr__(self):
        return '<TimetableType name="{}">'.format(self.name)

    def is_default(self):
        return self.default_type == self

    @classmethod
    def find_by_name(cls, name):
        for timetable in cls.timetable_types:
            if timetable.name == name:
                return timetable
        return None

    @classmethod
    def register(cls, name, route_name, display_name, is_default=False):
        timetable_type = cls(name, route_name, display_name)

        cls.timetable_types.append(timetable_type)

        if cls.default_type is None or is_default:
            cls.set_default(timetable_type)

        return timetable_type

    @classmethod
    def is_exist(cls, name):
        timetable_type = cls.find_by_name(name)
        return timetable_type is not None

    @classmethod
    def set_default(cls, default_type):
        """
        :type default_type: TimetableType
        :return:
        """
        cls.default_type = default_type


TimetableType.register('half_hourly', 'timetable.half_hourly', '30分区切り', is_default=True)
TimetableType.register('univ_tsukuba', 'timetable.univ_tsukuba', '筑波大学時間割')


class HalfHourlyTimetable():
    name = 'half_hourly'
    route_name = 'timetable.half_hourly'
    display_name = u'30分区切り'

    start_time = 800
    end_time = 2300

    _one_day = [
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

    timetable = [
        _one_day
        for i in
        range(7)
        ]


class UnivTsukubaTimetable():
    name = 'univ_tsukuba'
    route_name = 'timetable.univ_tsukuba'
    display_name = u'筑波大学時間割'

    start_time = 800
    end_time = 2300

    _workweek = [
        # 1st
        840,
        955,
        # 2nd
        1010,
        1125,
        # 3rd
        1215,
        1330,
        # 4th
        1345,
        1500,
        # 5th
        1515,
        1630,
        # 6th
        1645,
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
    _weekend = HalfHourlyTimetable._one_day

    timetable = [
        _workweek,
        _workweek,
        _workweek,
        _workweek,
        _workweek,
        _weekend,
        _weekend,
    ]
