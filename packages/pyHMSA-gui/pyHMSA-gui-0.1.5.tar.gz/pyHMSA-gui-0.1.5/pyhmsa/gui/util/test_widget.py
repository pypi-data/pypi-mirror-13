#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.util.widget import ColorDialogButton

# Globals and constants variables.

class TestColorDialogButton(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = ColorDialogButton()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        pass


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
