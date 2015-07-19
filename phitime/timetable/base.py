from xml.etree import ElementTree as ET
import datetime
import abc
import math


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


_START_TIME = None
_END_TIME = None


class SVGTimetable(metaclass=abc.ABCMeta):
    START_TIME = _START_TIME
    END_TIME = _END_TIME
    ROW_HEADER_WIDTH = 30

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
        svg.append(self.gen_row_header())
        for url in self.script_urls:
            script = self._create_script_elem(url)
            svg.append(script)
        root.append(svg)

        return root

    def _gen_viewbox(self):
        row_header_width = self.ROW_HEADER_WIDTH
        column_header_height = SVGDay.HEADER_HEIGHT
        timetable_width = sum(map(lambda day: day.WIDTH, self.days))
        timetable_height = conv2y(self.END_TIME) - conv2y(self.START_TIME)
        return '-{row_header_width} -{column_header_height} {width} {height}'.format(
            row_header_width=row_header_width,
            column_header_height=column_header_height,
            width=timetable_width + row_header_width,
            height=timetable_height + column_header_height,
        )

    def _to_elem(self):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        svg = ET.Element('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'viewBox': self._gen_viewbox(),
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

    def gen_row_header(self):
        header_elem = ET.Element('g', {
            'class': 'row_header',
            'transform': 'translate({},0)'.format(-self.ROW_HEADER_WIDTH)
        })
        start_hour = self.START_TIME // 100
        end_hour = math.ceil(float(self.END_TIME) / 100)
        y_offset = 0
        for hour, next_hour in zip(range(start_hour, end_hour), range(start_hour + 1, end_hour + 1)):
            if hour == start_hour:
                height = conv2y(next_hour * 100) - conv2y(self.START_TIME)
            elif next_hour == end_hour:
                height = conv2y(self.END_TIME) - conv2y(hour * 100)
            else:
                height = conv2y(100)
            elem = self._gen_header_elem(str(hour), height, y_offset)
            header_elem.append(elem)
            y_offset += height
        return header_elem

    def _gen_header_elem(self, header_text, height, y_offset):
        elem = ET.Element('g', {
            'transform': 'translate(0, {})'.format(y_offset),
        })
        rect = ET.Element('rect', {
            'width': self.ROW_HEADER_WIDTH,
            'height': height,
        })
        text = ET.Element('text', {
            'x': self.ROW_HEADER_WIDTH / 2,
            'y': height / 2,
        })
        text.text = header_text
        stringify_element_attribute(elem)
        stringify_element_attribute(rect)
        stringify_element_attribute(text)
        elem.append(rect)
        elem.append(text)
        return elem

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
    WIDTH = 90
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
            'y': self.HEADER_HEIGHT / 2,
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
