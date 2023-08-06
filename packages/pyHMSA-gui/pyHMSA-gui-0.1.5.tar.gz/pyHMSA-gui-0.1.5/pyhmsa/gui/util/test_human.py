#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from pyhmsa.gui.util.human import camelcase_to_words

# Globals and constants variables.

class TestModule(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testcamelcase_to_words(self):
        text = 'JohnDoe'
        actual = camelcase_to_words(text)
        expected = ('John', 'Doe')
        self.assertEqual(expected, actual)

        text = 'JohnDoeAndJaneDoe'
        actual = camelcase_to_words(text)
        expected = ('John', 'Doe', 'And', 'Jane', 'Doe')
        self.assertEqual(expected, actual)

        text = 'John'
        actual = camelcase_to_words(text)
        expected = ('John',)
        self.assertEqual(expected, actual)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
