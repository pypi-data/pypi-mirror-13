#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.spec.header import HeaderWidget

# Globals and constants variables.

class TestHeaderWidget(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

        self.wdg = HeaderWidget()

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def test_initui(self):
        QTest.keyClicks(self.wdg._txt_title, "Title")
        self.assertEqual("Title", self.wdg._txt_title.text())

        QTest.keyClicks(self.wdg._txt_author, 'Author')
        self.assertEqual("Author", self.wdg._txt_author.text())

        QTest.keyClicks(self.wdg._txt_owner, 'Owner')
        self.assertEqual("Owner", self.wdg._txt_owner.text())

        QTest.keyClicks(self.wdg._txt_timezone, 'Eastern')
        self.assertEqual("Eastern", self.wdg._txt_timezone.text())

        QTest.keyClicks(self.wdg._txt_checksum, 'check')
        self.assertIsNone(self.wdg._txt_checksum.text())

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
