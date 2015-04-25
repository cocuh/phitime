class TimetableType(object):
    timetable_types = []
    default_type = None
    
    def __init__(self, name, route_name, display_name_jp, display_name_en):
        self.name = name
        self.display_name_jp = display_name_jp
        self.display_name_en = display_name_en
        self.route_name = route_name
    
    @classmethod
    def find_by_name(cls, name):
        for timetable in cls.timetable_types:
            if timetable.name == name:
                return timetable
        return None
    
    @classmethod
    def register(cls, name, route_name, display_name_jp, display_name_en):
        timetable_type = cls(name, route_name, display_name_jp, display_name_en)
        
        if cls.default_type is None:
            cls.set_default(timetable_type)
        
        return timetable_type
    
    @classmethod
    def set_default(cls, default_type):
        """
        :type default_type: TimetableType
        :return:
        """
        cls.default_type = default_type

TimetableType.register('univ_tsukuba', 'timetable.univ_tsukuba',
    '筑波大学時間割', 'timetable of Univ.Tsukuba')

TimetableType.register('half_hourly', 'timetable.half_hourly',
    '30分区切り', 'half hourly timetable')

