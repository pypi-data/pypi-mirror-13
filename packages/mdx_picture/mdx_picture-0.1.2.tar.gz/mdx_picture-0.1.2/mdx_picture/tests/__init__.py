from __future__ import absolute_import
__version__ = '0.1.0'
__all__ = [
    'MdxPictureBlockParsingTest', 'MdxPictureBlockVadiationTest',
]

__author__ = 'Artem Grebenkin <speechkey@gmail.com>'

from .test_block_elem_order import MdxPictureBlockParsingTest
from .test_valid_block import MdxPictureBlockVadiationTest


import unittest


def get_suite():
    "Return a unittest.TestSuite."
    from mdx_picture import tests

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(tests)
    return suite
