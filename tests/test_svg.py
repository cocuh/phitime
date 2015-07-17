from . import BaseTestCase


class SVGElementTest(BaseTestCase):
    def _getTargetClass(self):
        from phitime.svg import SVGElement
        return SVGElement

    def _makeOne(self, tag, **extra):
        return self._getTargetClass()(tag, **extra)

    def test_append_child(self):
        elem = self._makeOne('g')

        self.assertEqual(len(elem), 0)

        target = elem.append_child('piyo')

        self.assertIsInstance(target, self._getTargetClass())
        self.assertEqual(len(elem), 1)

    def test_add_class(self):
        elem = self._makeOne('g')

        self.assertFalse(elem.has_class('hoge'))

        elem.add_class('hoge')

        self.assertTrue(elem.has_class('hoge'))

    def test_dump(self):
        elem = self._makeOne('g')
        elem.add_class('hoge')

        self.assertEqual(elem.tostring(), '<g class="hoge" />')


class SVGDocumentTest(BaseTestCase):
    def _getTargetClass(self):
        from phitime.svg import SVGDocument
        return SVGDocument

    def _makeOne(self, url=None, **attrib):
        return self._getTargetClass()(url, **attrib)

    def test_this(self):
        doc = self._makeOne('http://example.com/css/hoge.css')

        self.assertEqual(
            doc.tostring(),
            '<?xml-stylesheet type="text/css" href="http://example.com/css/hoge.css"?>\n' +
            '<svg xmlns="http://www.w3.org/2000/svg" />'
        )
