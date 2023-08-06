#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.testcase import TestCaseQApp, QTest
from pyhmsa.gui.util.registry import \
    (iter_entry_points,
     iter_condition_widget_classes, iter_condition_widgets,
     iter_datum_widget_classes, iter_datum_widgets,
     iter_importer_classes, iter_importers,
     iter_exporter_classes, iter_exporters,
     iter_preferences_widget_classes)

# Globals and constants variables.

class TestModule(TestCaseQApp):

    def setUp(self):
        TestCaseQApp.setUp(self)

    def tearDown(self):
        TestCaseQApp.tearDown(self)

    def testiter_entry_points(self):
        pass

    def testiter_condition_widget_classes(self):
        pass

    def testiter_condition_widgets(self):
        pass

    def testiter_datum_widget_classes(self):
        pass

    def testiter_datum_widgets(self):
        pass

    def testiter_importer_classes(self):
        pass

    def testiter_importers(self):
        pass

    def testiter_exporter_classes(self):
        pass

    def testiter_exporters(self):
        pass

    def testiter_preferences_widget_classes(self):
        pass


if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
