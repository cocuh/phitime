from phitime.timetable.base import TimetableType, ElementGenerationInfo
from phitime.timetable.strategy import ClassStrategy


class SVGTimetableRendererFactory(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        timetable = value.get('timetable')
        """:type: phitime.timetable.base.TimetableType"""
        if timetable is None:
            raise TypeError('no timetable argument')
        elif not isinstance(timetable, TimetableType):
            raise TypeError('timetable is not instance of TimetableType')

        event = value.get('event')
        """:type: phitime.models.Event"""
        if event is not None:
            timetable.set_event(event)
        
        request = system.get('request')
        """:type: pyramid.request.Request"""
        if request is not None:
            response = request.response
            response.content_type = 'image/svg+xml'

        strategies = value.get('class_strategies', [])
        """:type: list[phitime.timetable.strategy.BaseStrategy]"""

        class_strategy = ClassStrategy(strategies, event)

        return timetable.to_string(class_strategy)
