# -*- coding: utf-8 -*-
"""Test Propertyshelf MLS listings API."""

# python imports
import httpretty

# local imports
from mls.apiclient.client import ListingResource
from mls.apiclient.tests import base, utils


class TestCategories(base.BaseTestCase):
    """Listing categories test case."""
    PATH = '/api/listings/categories'

    @httpretty.httprettified
    def test_listing_types(self):
        resource = 'listing_types'
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.URL, resource),
            body=utils.load_fixture('category_listing_types_en.json')
        )
        client = ListingResource(self.BASE_URL)
        category = client.category(resource)
        assert httpretty.last_request().querystring == {
            'format': ['json'],
        }
        expected = [
            ('ll', 'Land Listing'),
            ('rl', 'Residential Lease'),
            ('rs', 'Residential Sale'),
        ]
        assert category == expected

    @httpretty.httprettified
    def test_view_types(self):
        resource = 'view_types'
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.URL, resource),
            body=utils.load_fixture('category_view_types_en.json')
        )
        client = ListingResource(self.BASE_URL)
        category = client.category(resource)
        assert httpretty.last_request().querystring == {
            'format': ['json'],
        }
        expected = [
            ('beach_view', 'Beach View'),
        ]
        assert category == expected
