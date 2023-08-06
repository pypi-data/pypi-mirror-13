#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.spec.datum.analysislist import \
    (AnalysisList0DTableWidget,
     AnalysisList1DGraphWidget, AnalysisList1DTableWidget,
     AnalysisList2DGraphWidget, AnalysisList2DTableWidget)

# Globals and constants variables.

class TestAnalysisList0DTableWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AnalysisList0DTableWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAnalysisList1DGraphWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AnalysisList1DGraphWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAnalysisList1DTableWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AnalysisList1DTableWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAnalysisList2DGraphWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AnalysisList2DGraphWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestAnalysisList2DTableWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = AnalysisList2DTableWidget(self.controller)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
