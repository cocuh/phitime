from xml.etree import ElementTree as ET
import datetime
import abc


def conv2y(time):
    hour = time // 100
    minute = time % 100
    assert 0 <= minute < 60
    return hour * 60 + minute


def stringify_element_attribute(elem):
    assert isinstance(elem, ET.Element)
    accepted_type = [str, int, float]
    for key, value in elem.attrib.items():
        if any(
                isinstance(value, ty)
                for ty in accepted_type
        ):
            elem.attrib[key] = str(value)
        else:
            raise TypeError('attr has invlaid type key:{} value:{}'.format(key, value))


_START_TIME = 800
_END_TIME = 2300


class SVGTimetable(metaclass=abc.ABCMeta):
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    def __init__(self, start_date, day_length, stylesheet_urls, script_urls):
        """
        :type date: datetime.date 
        :return:
        """
        self.start_date = start_date
        self.stylesheet_urls = stylesheet_urls
        self.script_urls = script_urls
        self.day_length = day_length
        self.days = self._gen_days()
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

        svg = self._to_elem()
        for url in self.script_urls:
            script = self._create_script_elem(url)
            svg.append(script)
        root.append(svg)

        return root

    def _to_elem(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'viewBox': '-30 -30 590 930',  # fixme
        })
        stringify_element_attribute(svg)
        main = ET.Element('g', {
            'id': 'main',
            'data-start': conv2y(self.START_TIME),
        })
        stringify_element_attribute(main)
        svg.append(main)
        for day in self.days:
            main.append(day.to_elem())
        return svg

    @staticmethod
    def _create_stylesheet_elem(stylesheet_url):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        # FIXME: it might have xss vulnerability
        stylesheet = ET.ProcessingInstruction('xml-stylesheet', 'type="text/css" href="{}"'.format(stylesheet_url))
        stylesheet.tail = "\n"
        return stylesheet

    def _gen_days(self):
        """
        :type start_date: datetime.date
        :type day_length: int
        :return:
        """
        start_date = self.start_date
        day_length = self.day_length
        days = []

        for day_idx in range(day_length):
            date = start_date + datetime.timedelta(day_idx)
            day = self.gen_day(date, day_idx)
            days.append(day)
        return days

    @abc.abstractmethod
    def gen_day(self, date, day_idx):
        """
        :type date: datetime.date
        :type day_idx: int 
        :rtype: SVGDay
        """
        raise NotImplemented()

    @staticmethod
    def _create_script_elem(url):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        # FIXME: it might have xss vulnerability
        stylesheet = ET.Element('script', {
            'type': 'application/javascript',
            'xlink:href': url,
        })
        stylesheet.tail = "\n"
        return stylesheet


class SVGDay(metaclass=abc.ABCMeta):
    WIDTH = 80
    HEADER_HEIGHT = 30
    START_TIME = _START_TIME
    END_TIME = _END_TIME

    def __init__(self, date, day_idx):
        self.date = date
        self.day_idx = day_idx
        self.weekday = self._get_weekday_identifier(date)
        self.periods = self.gen_periods()
        """:type: list[SVGPeriod]"""

    def to_elem(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        elem = self._to_elem()

        elem_header = self._gen_header_elem(self.weekday)  # fixme header text
        elem.append(elem_header)

        y_offset = 0
        for period in self.periods:
            period_elem = period.to_elem(self.WIDTH, y_offset)
            elem.append(period_elem)
            y_offset += period.height
        return elem

    @abc.abstractmethod
    def gen_periods(self):
        """
        override here
        :rtype: list[SVGPeriod]
        """
        raise NotImplementedError()

    def _gen_header_elem(self, header_text):
        elem = ET.Element('g', {
            'id': 'column_header_{}'.format(self.weekday),
            'data-day': self.weekday,
            'transform': 'translate(0,{y})'.format(
                y=-self.HEADER_HEIGHT
            ),
            'class': 'column_header',
        })
        rect = ET.Element('rect', {
            'width': self.WIDTH,
            'height': self.HEADER_HEIGHT,
        })
        text = ET.Element('text', {
            'x': self.WIDTH / 2,
            'y': 15,
        })
        text.text = self.gen_header_text()
        stringify_element_attribute(elem)
        stringify_element_attribute(text)
        stringify_element_attribute(rect)
        elem.append(rect)
        elem.append(text)
        return elem

    def _to_elem(self):
        elem = ET.Element('g', {
            'id': 'column_{}'.format(self.weekday),
            'data-day': self.weekday,
            'data-day-idx': self.day_idx,
            'class': 'column',
            'transform': 'translate({x},0)'.format(
                x=self.day_idx * self.WIDTH
            ),
        })
        stringify_element_attribute(elem)
        return elem

    @staticmethod
    def _get_weekday_identifier(date):
        """
        :type date: datetime.date 
        :rtype: str
        """
        return [
            "mon",
            "tue",
            "wed",
            "thr",
            "fri",
            "sat",
            "sun",
        ][date.weekday()]

    def gen_header_text(self):
        """
        generate header text.
        if change it, override this method.
        :rtype: str
        """
        month = self.date.month
        day = self.date.day
        weekday = self.date.strftime('%a')
        return '{month}/{day}({weekday})'.format(
            month=month,
            day=day,
            weekday=weekday,
        )


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
            'class': ' '.join(self.classes | {'cell'}),
            'data-day': self.day_idx,
            'data-y': self.start_y,
            'data-height': self.height,
            'transform': 'translate(0, {})'.format(y_offset),
        })
        rect = ET.Element('rect', {
            'width': width,
            'height': self.height,
        })
        stringify_element_attribute(elem)
        stringify_element_attribute(rect)
        elem.append(rect)
        return elem


class TimetableType(metaclass=abc.ABCMeta):
    display_name = None
    name = None
    route_name = None

    def to_string(self):
        raise NotImplementedError()
