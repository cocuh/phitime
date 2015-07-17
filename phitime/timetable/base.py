from phitime.svg import SVGDocument

from xml.etree import ElementTree as ET


class SVGTimetable():
    def __init__(self):
        self.root = SVGDocument()
        self.stylesheet_urls = []
        self.days = []
        """:type: list[SVGDay]"""

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
        # FIXME: it might be xss vulnerability
        stylesheet = ET.ProcessingInstruction('xml-stylesheet', 'type="text/css" href="{}"'.format(stylesheet_url))
        stylesheet.tail = "\n"
        return stylesheet


class SVGDay():
    WIDTH = 80
    HEADER_HEIGHT = 30

    def __init__(self):
        self.periods = []
        self.day_idx = 0
        self.day_identifier = 'mon'
        """:type: list[SVGPeriod]"""

    def to_elem(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        elem = self._to_elem()

        elem_header = self._gen_header(self.day_identifier)  # fixme header text
        elem.append(elem_header)

        y_offset = 0
        for period in self.periods:
            period_elem = period.to_elem(self.WIDTH, y_offset)
            elem.append(period_elem)
            y_offset += period.height
        return elem

    def _gen_header(self, header_text):
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


class SVGPeriod():
    def __init__(self, day_idx, start_time, end_time, classes=[]):
        self.day_idx = day_idx
        self.start_time = start_time
        self.end_time = end_time
        self.classes = set(classes)

    def add_class(self, classes):
        self.classes.update(classes)

    @property
    def height(self):
        """
        :rtype: int
        """
        return self.end_time - self.start_time

    def to_elem(self, width, y_offset):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        elem = ET.Element('g', {
            'classes': self.classes,
            'data-day': self.day_idx,
            'data-y': self.start_time - y_offset,
            'data-height': self.height,
            'transform': 'translate(0, {})'.format(y),
        })
        rect = ET.Element('g', {
            'width': width,
            'height': SVGDay.WIDTH,
        })
        elem.append(rect)
        return elem
