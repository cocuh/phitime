from xml.etree import ElementTree as ET


class SVGTree(ET.ElementTree):
    def write(self, **kwargs):
        pass


class SVGElement(ET.Element):
    def __init__(self, tag, attrib={}, **extra):
        self.classes = set()
        super().__init__(tag, attrib, **extra)

    def __setattr__(self, key, value):
        self.__dict__[key] = value

    def __getattr__(self, item):
        return self.__dict__[item]

    def add_class(self, *class_names):
        """
        :type class_names: set, str 
        :return:
        """
        self.classes.update(class_names)

    def has_class(self, class_name):
        return class_name in self.classes

    def makeelement(self, tag, attrib):
        return self.__class__(tag, attrib)

    def append_child(self, tag, attrib=None, **extra):
        if attrib is None:
            attrib = {}
        else:
            attrib = attrib.copy()
        attrib.update(extra)
        element = self.makeelement(tag, attrib)
        self.append(element)
        return element

    def tostring(self):
        self.set('class', ' '.join(self.classes))
        return ET.tostring(self, 'unicode')


class SVGDocument(SVGElement):
    def __init__(self, stylesheet_url=None, **attrib):
        if 'xmlns' not in attrib:
            attrib['xmlns'] = 'http://www.w3.org/2000/svg'

        super().__init__("svg", **attrib)

        # dummy root element for stylesheet object
        self.root = SVGElement(None, **attrib)

        if stylesheet_url:
            stylesheet = self._create_stylesheet(stylesheet_url)
            self.root.append(stylesheet)
        self.root.append(self)

    def tostring(self):
        return self.root.tostring()

    @staticmethod
    def _create_stylesheet(stylesheet_url):
        # FIXME: it might be xss vulnerability
        stylesheet = ET.ProcessingInstruction('xml-stylesheet', 'type="text/css" href="{}"'.format(stylesheet_url))
        stylesheet.tail = "\n"
        return stylesheet
