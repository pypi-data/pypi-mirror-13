#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.spec.datum.imageraster import \
    (ImageRaster2DGraphWidget, ImageRaster2DTableWidget,
     ImageRaster2DSpectralGraphWidget, ImageRaster2DSpectralTableWidget)

# Globals and constants variables.

class TestImageRaster2DGraphWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = ImageRaster2DGraphWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestImageRaster2DTableWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = ImageRaster2DTableWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestImageRaster2DSpectralGraphWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = ImageRaster2DSpectralGraphWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestImageRaster2DSpectralTableWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = ImageRaster2DSpectralTableWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
