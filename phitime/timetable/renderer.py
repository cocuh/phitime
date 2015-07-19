class SVGTimetableRendererFactory(object):
    def __init__(self, info):
        pass

    def __call__(self, value, system):
        timetable = value.get('timetable')
        request = system.get('request')
        if request is not None:
            response = request.response
            response.content_type = 'image/svg+xml'
        return timetable.to_string()
