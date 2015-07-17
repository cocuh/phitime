from xml.etree import ElementTree as ET

ET.SubElement()

class SVGTree(ET.ElementTree):
    def write(self, **kwargs):
        pass


class SVGElement(ET.Element):
    def __init__(self, tag, **extra):
        super().__init__(tag, **extra)
        self.classes = set()

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
    

class SVGDocument(SVGElement):
    def __init__(self, stylesheet_url, **attrib):
        super().__init__(None)

        tag = 'svg'
        if 'xmlns' not in attrib:
            attrib['xmlns'] = 'http://www.w3.org/2000/svg',

        stylesheet = self._create_stylesheet(stylesheet_url)
        svg = ET.Element(tag, **attrib)
        self.add_class(stylesheet)
        self.add_class(svg)

    def dump(self):
        self.set('class', ' '.join(self.classes))
        ET.dump(self)

    @staticmethod
    def _create_stylesheet(stylesheet_url):
        # FIXME: it might be xss vulnerability
        stylesheet = ET.ProcessingInstruction('xml-stylesheet', 'type="text/css" href="{}"'.format(stylesheet_url))
        stylesheet.tail = "\n"
        return stylesheet
