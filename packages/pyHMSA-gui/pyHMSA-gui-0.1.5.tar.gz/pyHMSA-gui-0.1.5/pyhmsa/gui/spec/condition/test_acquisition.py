#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.spec.condition.acquisition import \
    (AcquisitionPointWidget, AcquisitionMultipointWidget,
     AcquisitionRasterLinescanWidget, AcquisitionRasterXYWidget,
     AcquisitionRasterXYZWidget)

# Globals and constants variables.

class TestAcquisitionPointWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AcquisitionPointWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAcquisitionMultipointWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AcquisitionMultipointWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAcquisitionRasterLinescanWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AcquisitionRasterLinescanWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAcquisitionRasterXYWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AcquisitionRasterXYWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAcquisitionRasterXYZWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AcquisitionRasterXYZWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
