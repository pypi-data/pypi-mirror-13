#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.spec.condition.calibration import \
    (CalibrationConstantWidget, CalibrationLinearWidget,
     CalibrationPolynomialWidget, CalibrationExplicitWidget, CalibrationWidget)

# Globals and constants variables.

class TestCalibrationConstantWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = CalibrationConstantWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestCalibrationLinearWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = CalibrationLinearWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestCalibrationPolynomialWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = CalibrationPolynomialWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestCalibrationExplicitWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = CalibrationExplicitWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestCalibrationWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = CalibrationWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()