#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.util.periodictable import \
    ElementPushButton, PeriodicTableDialog, PeriodicTableWidget

# Globals and constants variables.

class TestElementPushButton(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = ElementPushButton(13)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestPeriodicTableDialog(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.dlg = PeriodicTableDialog()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

class TestPeriodicTableWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = PeriodicTableWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
