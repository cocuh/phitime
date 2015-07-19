from xml.etree import ElementTree as ET
import datetime
import abc
import math


def conv2y(time):
    hour = time // 100
    minute = time % 100
    assert 0 <= minute < 60
    return hour * 60 + minute


class SVGElement(ET.Element):
    def __init__(self, tag, attrib={}, **extra):
        attrib.update(extra)
        attrib = self._stringify_attrib(attrib)
        super().__init__(tag, attrib)

    def set(self, key, value):
        self.attrib[key] = self._stringify_value(value)

    def _stringify_value(self, value):
        if isinstance(value, str):
            return value
        elif isinstance(value, int) or isinstance(value, float):
            return str(value)
        else:
            raise TypeError('attr has invalid type value:{}'.format(value))

    def _stringify_attrib(self, attrib):
        for key, value in attrib.items():
            try:
                attrib[key] = self._stringify_value(value)
            except TypeError:
                raise TypeError('attr has invalid type key:{} value:{}'.format(key, value))
        return attrib


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
        root = SVGElement(None)

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
        svg = SVGElement('svg', {
            'xmlns': 'http://www.w3.org/2000/svg',
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'viewBox': self._gen_viewbox(),
        })
        main = SVGElement('g', {
            'id': 'main',
            'data-start': conv2y(self.START_TIME),
        })
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
        header_elem = SVGElement('g', {
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
        elem = SVGElement('g', {
            'transform': 'translate(0, {})'.format(y_offset),
        })
        rect = SVGElement('rect', {
            'width': self.ROW_HEADER_WIDTH,
            'height': height,
        })
        text = SVGElement('text', {
            'x': self.ROW_HEADER_WIDTH / 2,
            'y': height / 2,
        })
        text.text = header_text
        elem.append(rect)
        elem.append(text)
        return elem

    @staticmethod
    def _create_script_elem(url):
        """
        :rtype: xml.etree.ElementTree.Element
        """
        # FIXME: it might have xss vulnerability
        stylesheet = SVGElement('script', {
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
        elem = SVGElement('g', {
            'data-day': self.weekday,
            'transform': 'translate(0,{y})'.format(
                y=-self.HEADER_HEIGHT
            ),
            'class': ' '.join(['column_header', 'column_header_{}'.format(self.weekday)]),
        })
        rect = SVGElement('rect', {
            'width': self.WIDTH,
            'height': self.HEADER_HEIGHT,
        })
        text = SVGElement('text', {
            'x': self.WIDTH / 2,
            'y': self.HEADER_HEIGHT / 2,
        })
        text.text = self.gen_header_text()
        elem.append(rect)
        elem.append(text)
        return elem

    def _to_elem(self):
        elem = SVGElement('g', {
            'data-day': self.weekday,
            'data-day-idx': self.day_idx,
            'class': ' '.join(['column', 'column_{}'.format(self.weekday)]),
            'transform': 'translate({x},0)'.format(
                x=self.day_idx * self.WIDTH
            ),
        })
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
        elem = SVGElement('g', {
            'class': ' '.join(self.classes | {'cell'}),
            'data-day': self.day_idx,
            'data-y': self.start_y,
            'data-height': self.height,
            'transform': 'translate(0, {})'.format(y_offset),
        })
        rect = SVGElement('rect', {
            'width': width,
            'height': self.height,
        })
        elem.append(rect)
        return elem


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


class TimetableType(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def get_name(cls):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_display_name(cls):
        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def get_route_name(cls):
        raise NotImplementedError()

    @abc.abstractmethod
    def to_string(self):
        raise NotImplementedError()

    @classproperty
    def name(cls):
        return cls.get_name()

    @classproperty
    def route_name(cls):
        return cls.get_route_name()

    @classproperty
    def display_name(cls):
        return cls.get_display_name()


__all__ = [
    'SVGElement',
    'SVGTimetable',
    'SVGDay',
    'SVGPeriod',
    'TimetableType',
]
