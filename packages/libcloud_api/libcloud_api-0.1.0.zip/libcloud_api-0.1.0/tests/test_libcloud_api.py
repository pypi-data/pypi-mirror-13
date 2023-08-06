#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_libcloud.api
----------------------------------

Tests for `libcloud.api` module.
"""

import unittest

from libcloud_api import libcloud_api


class TestApi(unittest.TestCase):

    def setUp(self):
        self.api = libcloud_api()

    def tearDown(self):
        pass

    def test_000_something(self):
        pass


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
