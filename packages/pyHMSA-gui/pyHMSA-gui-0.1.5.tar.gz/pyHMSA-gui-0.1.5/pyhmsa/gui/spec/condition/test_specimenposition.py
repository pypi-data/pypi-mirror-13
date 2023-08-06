#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.spec.condition.specimenposition import \
    SpecimenPositionWidget, SpecimenPositionListWidget

# Globals and constants variables.

class TestSpecimenPositionWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = SpecimenPositionWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestSpecimenPositionListWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = SpecimenPositionListWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()