"""
Provides graphical components to construct graphical interface based on 
the Python implementation of the HMSA file format, pyHMSA.
"""

__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__copyright__ = "Copyright (c) 2013-2015 Philippe T. Pinard"
__license__ = "MIT"

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

# This is required to create a namespace package.
# A namespace package allows programs to be located in different directories or
# eggs.

__import__('pkg_resources').declare_namespace(__name__)
