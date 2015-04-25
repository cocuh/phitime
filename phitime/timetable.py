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
    def set_default(cls, default_type):
        """
        :type default_type: TimetableType
        :return:
        """
        cls.default_type = default_type


TimetableType.register('half_hourly', 'timetable.half_hourly', '30分区切り', is_default=True)
TimetableType.register('univ_tsukuba', 'timetable.univ_tsukuba', '筑波大学時間割')

