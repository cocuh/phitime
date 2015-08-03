from phitime.timetable.base import TimetableType
from phitime.timetable.strategy import ClassStrategyList


class SVGTimetableRendererFactory(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        request = system.get('request')
        """:type: pyramid.request.Request"""
        if request is not None:
            response = request.response
            response.content_type = 'image/svg+xml'

        event = value.get('event')
        """:type: phitime.models.Event|None"""
        member = value.get('member')
        """:type: phitime.models.Member|None"""

        if 'timetable' in value:
            timetable = value.get('timetable')
            """:type: phitime.timetable.base.TimetableType"""
            if timetable is None:
                raise TypeError('no timetable argument')
            elif not isinstance(timetable, TimetableType):
                raise TypeError('timetable is not instance of TimetableType')
        else:
            if 'stylesheet_urls' in value:
                stylesheet_urls = value.get('stylesheet_urls')
            else:
                stylesheet_urls = [request.static_path("phitime:static/timetables/univ_tsukuba_timetable.css")]
            if 'script_urls' in value:
                script_urls = value.get('script_urls')
            else:
                script_urls = []
                if value.get('is_editable'):
                    script_urls.append(request.static_path("phitime:static/timetables/timetable.js"))

            page = value.get('page')

            timetable = event.timetable_type.gen_instance(
                event, stylesheet_urls, script_urls, page)

        strategies = value.get('class_strategies', [])
        """:type: list[phitime.timetable.strategy.BaseStrategy]"""

        class_strategy_list = ClassStrategyList(strategies, event, member)

        return timetable.to_string(class_strategy_list)
