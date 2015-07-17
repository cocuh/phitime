from xml.etree import ElementTree as ET


def conv2y(time):
    hour = time // 100
    minute = time % 100
    assert 0 <= minute < 60
    return hour * 60 + minute


_START_TIME = 800
_END_TIME = 2300


class SVGTimetable(object):
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    def __init__(self, start_date):
        """
        :type date: datetime.date 
        :return:
        """
        self.start_date = start_date
        self.stylesheet_urls = []
        self.days = self.gen_days(start_date)
        """:type: list[SVGDay]"""

    def to_string(self):
        return ET.tostring(self.to_elem(), 'unicode')

    def to_elem(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        root = ET.Element(None)

        for url in self.stylesheet_urls:
            stylesheet = self._create_stylesheet_elem(url)
            root.append(stylesheet)

        elem = self._to_elem()
        root.append(elem)

        return root

    def _to_elem(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        elem = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/200/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'viewBox': '-30 -30 590 930',  # fixme
        })
        for day in self.days:
            elem.append(day.to_elem())
        return elem

    @staticmethod
    def _create_stylesheet_elem(stylesheet_url):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        # FIXME: it might have xss vulnerability
        stylesheet = ET.ProcessingInstruction('xml-stylesheet', 'type="text/css" href="{}"'.format(stylesheet_url))
        stylesheet.tail = "\n"
        return stylesheet

    def gen_days(self, start_date):
        raise NotImplementedError()


class SVGDay(object):
    WIDTH = 80
    HEADER_HEIGHT = 30
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    def __init__(self, date):
        self.date = date
        self.day_idx = 0
        self.day_identifier = 'mon'
        self.periods = self.gen_periods()
        """:type: list[SVGPeriod]"""

    def to_elem(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        elem = self._to_elem()

        elem_header = self._gen_header_elem(self.day_identifier)  # fixme header text
        elem.append(elem_header)

        y_offset = 0
        for period in self.periods:
            period_elem = period.to_elem(self.WIDTH, y_offset)
            elem.append(period_elem)
            y_offset += period.height
        return elem

    def gen_periods(self):
        """
        override here
        :rtype: list[SVGPeriod]
        """
        # TODO use abc
        raise NotImplementedError()

    def _gen_header_elem(self, header_text):
        elem = ET.Element('g', {
            'id': 'column_header_{}'.format(self.day_identifier),
            'data-day': self.day_identifier,
            'transform': 'translate(0,{y})'.format(
                y=-self.HEADER_HEIGHT
            ),
            'class': 'column_header',
        })
        elem_rect = ET.Element('rect', {
            'width': self.WIDTH,
            'height': self.HEADER_HEIGHT,
        })
        elem_text = ET.Element('text', {
            'x': self.WIDTH / 2,
            'y': 15,
        })
        elem_text.text = header_text
        elem.append(elem_rect)
        elem.append(elem_text)
        return elem

    def _to_elem(self):
        elem = ET.Element('g', {
            'id': 'column_{}'.format(self.day_identifier),
            'data-day': self.day_identifier,
            'transform': 'translate({x},0)'.format(
                x=self.day_idx * self.WIDTH
            ),
        })
        return elem


class SVGPeriod(object):
    def __init__(self, day_idx, start_time, end_time, classes=[]):
        self.day_idx = day_idx
        self.start_y = conv2y(start_time)
        self.end_y = conv2y(end_time)
        self.classes = set(classes)

    def add_class(self, classes):
        self.classes.update(classes)

    @property
    def height(self):
        """
        :rtype: int
        """
        return self.end_y - self.start_y

    def to_elem(self, width, y_offset):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        elem = ET.Element('g', {
            'classes': self.classes,
            'data-day': self.day_idx,
            'data-y': self.start_y - y_offset,
            'data-height': self.height,
            'transform': 'translate(0, {})'.format(y),
        })
        rect = ET.Element('g', {
            'width': width,
            'height': SVGDay.WIDTH,
        })
        elem.append(rect)
        return elem


class TimetableType(object):
    pass
