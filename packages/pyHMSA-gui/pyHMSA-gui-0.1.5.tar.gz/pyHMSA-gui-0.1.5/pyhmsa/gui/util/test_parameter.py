#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.util.parameter import \
    (TextAttributeLineEdit, NumericalAttributeLineEdit, UnitAttributeLineEdit,
     AtomicNumberAttributePushButton, ParameterWidget)

from pyhmsa.spec.condition.detector import DetectorSpectrometer
from pyhmsa.spec.condition.elementalid import ElementalID

# Globals and constants variables.

class TestTextAttributeLineEdit(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        attribute = DetectorSpectrometer.serial_number
        self.wdg = TextAttributeLineEdit(attribute)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestNumericalAttributeLineEdit(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        attribute = DetectorSpectrometer.elevation
        self.wdg = NumericalAttributeLineEdit(attribute)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestUnitAttributeLineEdit(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        attribute = DetectorSpectrometer.measurement_unit
        self.wdg = UnitAttributeLineEdit(attribute)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAtomicNumberAttributePushButton(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        attribute = ElementalID.atomic_number
        self.wdg = AtomicNumberAttributePushButton(attribute)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestParameterWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = ParameterWidget(DetectorSpectrometer)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
