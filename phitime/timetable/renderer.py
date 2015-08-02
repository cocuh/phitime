from phitime.timetable.base import TimetableType, ElementGenerationInfo


class SVGTimetableRendererFactory(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        timetable = value.get('timetable')
        """:type: phitime.timetable.base.TimetableType"""
        if timetable is None:
            raise TypeError('no timetable argument')
        elif isinstance(timetable, TimetableType):
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

        gen_info = self._create_gen_info(event=event)

        return timetable.to_string(gen_info)

    @staticmethod
    def _create_gen_info(event=None):
        gen_info = ElementGenerationInfo()
        if event is not None:
            gen_info.set_event(event)
        return gen_info
