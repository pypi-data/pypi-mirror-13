# -*- coding: utf-8 -*-
"""Test utility methods."""

# local imports
from mls.apiclient import utils
from mls.apiclient.tests import base


class TestUtils(base.BaseTestCase):
    """Util methods Test Case."""

    def test_extract_headers(self):
        headers = {
            'prefix1-header1': 'value1',
            'prefix1-header2': 'value2',
            'prefix2-header3': 'value3',
            'prefix1-header4': 'value4',
        }
        result = utils.extract_headers(headers, 'prefix1')
        self.assertEqual(result, {
            'header1': 'value1',
            'header2': 'value2',
            'header4': 'value4',
        })

        result = utils.extract_headers(headers, 'prefix2')
        self.assertEqual(result, {'header3': 'value3'})

        result = utils.extract_headers(headers, 'prefix3')
        self.assertEqual(result, {})
