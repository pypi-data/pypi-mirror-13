#!/usr/bin/env python
""" """

# Standard library modules.
import unittest

# Third party modules.
from qtpy.QtWidgets import QApplication
from qtpy.QtCore import QObject

try:
    from qtpy.QtTest import QTest #@UnusedImport
except ImportError:
    # Override qtpy which says that PySide's QTest does not work
    from PySide.QtTest import QTest #@UnusedImport

# Local modules.
from pyhmsa.gui.util.settings import Settings

# Globals and constants variables.

class MockController(QObject):

    def __init__(self):
        self._settings = Settings("HMSA", "testcase")

    @property
    def settings(self):
        return self._settings

_instance = None

class TestCaseQApp(unittest.TestCase):
    '''Helper class to provide QApplication instances'''

    qapplication = True

    def setUp(self):
        super().setUp()
        global _instance
        if _instance is None:
            _instance = QApplication([])

        self.app = _instance
        self.controller = MockController()

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.app
        super().tearDown()
