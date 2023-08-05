# -*- coding: utf-8 -*-
"""Test the resource classes."""

# python imports
import httpretty
import json

# local imports
from mls.apiclient import api, resources
from mls.apiclient.tests import base, utils
from mls.apiclient.utils import join_url


class ResourceTestCase(base.BaseTestCase):
    """Test resource class."""

    def setUp(self):
        self.api = api.API(self.BASE_URL)
        self.data = json.loads(utils.load_fixture('basic_single.json'))

    def _callFUT(self, api, data):
        return resources.Resource(api, data)

    def test_wrong_data(self):
        """Validate the ValueError if data is not a dictionary."""
        self.assertRaises(ValueError, self._callFUT, self.api, None)
        self.assertRaises(ValueError, self._callFUT, self.api, 1)
        self.assertRaises(ValueError, self._callFUT, self.api, 1.1)
        self.assertRaises(ValueError, self._callFUT, self.api, True)
        self.assertRaises(ValueError, self._callFUT, self.api, 'Foo')
        self.assertRaises(ValueError, self._callFUT, self.api, u'Foo')

    def test_correct_data(self):
        """Validate the correct initialization with a dictionary."""
        data = {
            'response': {
                'foo': 'bar',
            },
        }
        foo = self._callFUT(self.api, data)
        self.assertIsInstance(foo, resources.Resource)
        self.assertEqual(data.get('response'), foo._data)

    def test_attributes(self):
        """Validate the content of the data dictionary."""
        data = {
            'response': {
                'foo': 'bar',
            },
        }
        foo = self._callFUT(self.api, data)
        self.assertEqual(foo.foo, 'bar')

    def test_missing_attributes(self):
        """Validate that an error is raised when an attribute is missing."""
        data = {
            'response': {
                'foo': 'bar',
            },
        }
        foo = self._callFUT(self.api, data)
        self.assertRaises(AttributeError, getattr, foo, 'bar')

    def test_get_attributes(self):
        """Validate the output of the get_attributes method."""
        data = {
            'response': {
                'foo': 'bar',
                'baz': 'barbar',
            },
        }
        foo = self._callFUT(self.api, data)
        result = foo.get_attributes()
        self.assertIn('foo', result)
        self.assertIn('baz', result)
        self.assertEqual(len(result), 2)

        foo = self._callFUT(self.api, self.data)
        result = foo.get_attributes()
        self.assertIn('id', result)
        self.assertIn('links', result)
        self.assertEqual(len(result), 2)

    def test_get_id(self):
        """Validate the output of the get_id method."""
        foo = self._callFUT(self.api, {})
        self.assertIsNone(foo.get_id())

        data = {
            'response': {
                'id': 'my_id',
            },
        }
        foo = self._callFUT(self.api, data)
        self.assertEqual(foo.get_id(), 'my_id')

        foo = self._callFUT(self.api, self.data)
        self.assertEqual(foo.get_id(), 'test_id')

    def test_get_url(self):
        """Validate the output of the get_url method."""
        foo = self._callFUT(self.api, {})
        self.assertIsNone(foo.get_url())

        data = {
            'response': {
                'links': [{
                    'href': 'http://example.com',
                    'rel': 'next',
                    'method': 'GET',
                }]
            }
        }
        foo = self._callFUT(self.api, data)
        self.assertIsNone(foo.get_url())

        data = {
            'response': {
                'links': [{
                    'href': 'http://example.com',
                    'rel': 'self',
                    'method': 'GET',
                }]
            }
        }
        foo = self._callFUT(self.api, data)
        self.assertEqual(foo.get_url(), 'http://example.com')

        foo = self._callFUT(self.api, self.data)
        self.assertEqual(
            foo.get_url(),
            'http://demomls.com/api/rest/v1/test_url',
        )

    def test_headers(self):
        """Validate the headers of the response."""
        foo = self._callFUT(self.api, {})
        self.assertEqual(foo.get_headers(), {})

        data = {
            'headers': {
                'header-1': 'value1',
                'header-2': 'value2',
            },
        }
        foo = self._callFUT(self.api, data)
        headers = foo.get_headers()
        self.assertIn('header-1', headers)
        self.assertIn('header-2', headers)
        self.assertEqual(len(headers), 2)

        foo = self._callFUT(self.api, self.data)
        headers = foo.get_headers()
        self.assertIn('result-single', headers)
        self.assertTrue(headers.get('result-single'))
        self.assertEqual(len(headers), 1)


class AgencyTestCase(base.BaseTestCase):
    """Test 'Agency' resource class."""

    def setUp(self):
        self.api = api.API(self.BASE_URL)

    def _callFUT(self, api, data):
        return resources.Agency(api, data)

    def test_listings(self):
        """Validate the listing search for agencies."""
        agency = self._callFUT(self.api, {})
        self.assertRaises(NotImplementedError, agency.listings)

    def test_developments(self):
        """Validate the development search for agencies."""
        agency = self._callFUT(self.api, {})
        self.assertRaises(NotImplementedError, agency.developments)


class AgentTestCase(base.BaseTestCase):
    """Test 'Agent' resource class."""

    def setUp(self):
        self.api = api.API(self.BASE_URL)

    def _callFUT(self, api, data):
        return resources.Agent(api, data)

    def test_listings(self):
        """Validate the listing search for agents."""
        agent = self._callFUT(self.api, {})
        self.assertRaises(NotImplementedError, agent.listings)


class DevelopmentTestCase(base.BaseTestCase):
    """Test 'Development' resource class."""

    endpoint = 'developments'

    def setUp(self):
        self.api = api.API(self.BASE_URL)

    def _callFUT(self, api, data):
        return resources.Development(api, data)

    @httpretty.httprettified
    def test_get_development(self):
        """Validate the 'get' endpoint."""
        dev_id = 'dev-agency__dev001'
        resource = join_url(self.endpoint, dev_id)
        response = utils.load_fixture('development_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.Development.get(self.api, dev_id)
        self.assertIsInstance(result, resources.Development)
        response_dict = json.loads(response)
        self.assertEqual(result._data, response_dict.get('response'))

    @httpretty.httprettified
    def test_get_all(self):
        """Validate the 'search' endpoint to get all developments."""
        resource = self.endpoint
        response = utils.load_fixture('development_list_1.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.Development.search(self.api)
        self.assertIsInstance(result, resources.Development)
        response_dict = json.loads(response)
        self.assertEqual(result._data, response_dict.get('response'))

    def test_get_items_development(self):
        """Validate the 'search' endpoint to get all developments and get the
        list of developments from the result.
        """
        data_single = json.loads(utils.load_fixture('development_en.json'))
        development = self._callFUT(self.api, data_single)
        items = development.get_items()
        self.assertEqual(len(items), 0)

        data_list = json.loads(utils.load_fixture('development_list_1.json'))
        development = self._callFUT(self.api, data_list)
        items = development.get_items()
        self.assertEqual(len(items), 1)
        for item in items:
            self.assertIsInstance(item, resources.Development)
            self.assertEqual(item._data, data_single.get('response'))

    @httpretty.httprettified
    def test_development_fields(self):
        """Validate the 'field_titles' endpoint."""
        resource = join_url('field_titles', self.endpoint)
        response = utils.load_fixture('development_fields_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.Development.get_field_titles(self.api)
        self.assertEqual(result, json.loads(response))

    @httpretty.httprettified
    def test_development_field_order(self):
        """Validate the 'field_order' endpoint."""
        resource = join_url('field_order', self.endpoint)
        response = utils.load_fixture('development_fields_order.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.Development.get_field_order(self.api)
        self.assertEqual(result, json.loads(response))

    def test_listings(self):
        """Validate the listing search for developments."""
        development = self._callFUT(self.api, {})
        self.assertIsNone(development.listings())

    def test_listings_url(self):
        """Validate the deprecated listing search for developments."""
        data = json.loads(utils.load_fixture('development_en.json'))
        development = self._callFUT(self.api, data)
        self.assertEqual(
            development.listings_url,
            'http://demomls.com/api/listings/search?lang=en'
            '&apikey=YOUR_API_KEY&development_listings=dev-agency__dev001',
        )

    def test_pictures(self):
        """Validate the pictures for developments."""
        data = json.loads(utils.load_fixture('development_en.json'))
        development = self._callFUT(self.api, data)
        images = development.pictures()
        self.assertIsInstance(images, list)
        self.assertEqual(len(images), 2)
        for image in images:
            self.assertIsInstance(image, resources.Image)

    @httpretty.httprettified
    def test_property_groups(self):
        """Validate the property group search for developments."""
        data = json.loads(utils.load_fixture('development_en.json'))
        development = self._callFUT(self.api, data)

        resource = join_url(self.endpoint, development.get_id(), 'groups')
        response = utils.load_fixture('group_list_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        groups = development.groups()
        self.assertEqual(len(groups), 2)
        for group in groups:
            self.assertIsInstance(group, resources.PropertyGroup)

    @httpretty.httprettified
    def test_development_phases(self):
        """Validate the development phase search for developments."""
        data = json.loads(utils.load_fixture('development_en.json'))
        development = self._callFUT(self.api, data)

        resource = join_url(self.endpoint, development.get_id(), 'phases')
        response = utils.load_fixture('phase_list_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        phases = development.phases()
        self.assertEqual(len(phases), 2)
        for phase in phases:
            self.assertIsInstance(phase, resources.DevelopmentPhase)


class DevelopmentPhaseTestCase(base.BaseTestCase):
    """Test 'Development Phase' resource class."""

    endpoint = 'development_phases'

    def setUp(self):
        self.api = api.API(self.BASE_URL)

    def _callFUT(self, api, data):
        return resources.DevelopmentPhase(api, data)

    @httpretty.httprettified
    def test_phase_fields(self):
        """Validate the 'field_titles' endpoint."""
        resource = join_url('field_titles', self.endpoint)
        response = utils.load_fixture('phase_fields_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.DevelopmentPhase.get_field_titles(self.api)
        self.assertEqual(result, json.loads(response))

    @httpretty.httprettified
    def test_phase_field_order(self):
        """Validate the 'field_order' endpoint."""
        resource = join_url('field_order', self.endpoint)
        response = utils.load_fixture('phase_fields_order.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.DevelopmentPhase.get_field_order(self.api)
        self.assertEqual(result, json.loads(response))

    @httpretty.httprettified
    def test_get_all(self):
        """Validate the 'search' endpoint to get all phases."""
        resource = self.endpoint
        response = utils.load_fixture('phase_list_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.DevelopmentPhase.search(self.api)
        self.assertIsInstance(result, resources.DevelopmentPhase)
        response_dict = json.loads(response)
        self.assertEqual(result._data, response_dict.get('response'))

    @httpretty.httprettified
    def test_get_items_phases(self):
        """Validate the 'search' endpoint to get all phases and get the
        list of phases from the result.
        """
        resource = self.endpoint
        response = utils.load_fixture('phase_list_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.DevelopmentPhase.search(self.api)
        items = result.get_items()
        self.assertEqual(len(items), 2)
        for item in items:
            self.assertIsInstance(item, resources.DevelopmentPhase)
            self.assertIn('title', item._data)
            self.assertIn('units', item._data)
            self.assertIn('unit_types', item._data)
            self.assertIn('status', item._data)
            self.assertIn('listings_url', item._data)

    def test_listings(self):
        """Validate the listing search for development phases."""
        phase = self._callFUT(self.api, {})
        self.assertIsNone(phase.listings())

    def test_listings_url(self):
        """Validate the deprecated listing search for development phases."""
        data = json.loads(utils.load_fixture('phase_list_en.json'))
        phase_list = self._callFUT(self.api, data)
        phase = phase_list.get_items()[0]
        self.assertEqual(
            phase.listings_url,
            'http://demomls.com/api/listings/search?'
            'apikey=YOUR_API_KEY&phase_listings=dev-agency__dev001__phase-1',
        )


class ListingTestCase(base.BaseTestCase):
    """Test 'Listing' resource class."""

    def setUp(self):
        self.api = api.API(self.BASE_URL)

    def _callFUT(self, api, data):
        return resources.Listing(api, data)

    def test_pictures(self):
        """Validate the pictures for listings."""
        listing = self._callFUT(self.api, {})
        self.assertRaises(NotImplementedError, listing.pictures)


class PropertyGroupTestCase(base.BaseTestCase):
    """Test 'Property Group' resource class."""

    endpoint = 'property_groups'

    def setUp(self):
        self.api = api.API(self.BASE_URL)

    def _callFUT(self, api, data):
        return resources.PropertyGroup(api, data)

    @httpretty.httprettified
    def test_group_fields(self):
        """Validate the 'field_titles' endpoint."""
        resource = join_url('field_titles', self.endpoint)
        response = utils.load_fixture('group_fields_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.PropertyGroup.get_field_titles(self.api)
        self.assertEqual(result, json.loads(response))

    @httpretty.httprettified
    def test_group_field_order(self):
        """Validate the 'field_order' endpoint."""
        resource = join_url('field_order', self.endpoint)
        response = utils.load_fixture('group_fields_order.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.PropertyGroup.get_field_order(self.api)
        self.assertEqual(result, json.loads(response))

    @httpretty.httprettified
    def test_get_all(self):
        """Validate the 'search' endpoint to get all property groups."""
        resource = self.endpoint
        response = utils.load_fixture('group_list_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.PropertyGroup.search(self.api)
        self.assertIsInstance(result, resources.PropertyGroup)
        response_dict = json.loads(response)
        self.assertEqual(result._data, response_dict.get('response'))

    @httpretty.httprettified
    def test_get_items_groups(self):
        """Validate the 'search' endpoint to get all groups and get the
        list of groups from the result.
        """
        resource = self.endpoint
        response = utils.load_fixture('group_list_en.json')
        httpretty.register_uri(
            httpretty.GET,
            utils.get_url(self.API_BASE, resource),
            body=response,
        )
        result = resources.PropertyGroup.search(self.api)
        items = result.get_items()
        self.assertEqual(len(items), 2)
        for item in items:
            self.assertIsInstance(item, resources.PropertyGroup)
            self.assertIn('title', item._data)
            self.assertIn('status', item._data)
            self.assertIn('listings_url', item._data)

    def test_listings(self):
        """Validate the listing search for property groups."""
        group = self._callFUT(self.api, {})
        self.assertIsNone(group.listings())

    def test_listings_url(self):
        """Validate the deprecated listing search for property groups."""
        data = json.loads(utils.load_fixture('group_list_en.json'))
        group_list = self._callFUT(self.api, data)
        group = group_list.get_items()[0]
        self.assertEqual(
            group.listings_url,
            'http://demomls.com/api/listings/search?property_group_listings'
            '=dev-agency__dev001__classy&apikey=YOUR_API_KEY'
        )


class ImageTestCase(base.BaseTestCase):
    """Test 'Image' resource class."""

    def setUp(self):
        self.data = {
            'large': 'http://demo.com/pics/img1/@@scaling/img1-large.jpeg',
            'tile': 'http://demo.com/pics/img1/@@scaling/img1-tile.jpeg',
            'thumb': 'http://demo.com/pics/img1/@@scaling/img1-thumb.jpeg',
            'title': 'Title of image 1',
            'url': 'http://demo.com/pics/img1/@@scaling/img1-url.jpeg',
            'preview': 'http://demo.com/pics/img1/@@scaling/img1-preview.jpeg',
            'id': 'img1',
            'description': 'Description of image 1',
        }

    def _callFUT(self, data):
        return resources.Image(data)

    def test_title(self):
        """Validate the 'title' attribute of Images."""
        image = self._callFUT(self.data)
        self.assertEqual(image.title, 'Title of image 1')

    def test_id(self):
        """Validate the 'id' attribute of Images."""
        image = self._callFUT(self.data)
        self.assertEqual(image.id, 'img1')

    def test_description(self):
        """Validate the 'description' attribute of Images."""
        image = self._callFUT(self.data)
        self.assertEqual(image.description, 'Description of image 1')

    def test_get_large(self):
        """Validate getting the 'large' scale url."""
        image = self._callFUT(self.data)
        self.assertEqual(
            image.get('large'),
            'http://demo.com/pics/img1/@@scaling/img1-large.jpeg',
        )

    def test_get_tile(self):
        """Validate getting the 'tile' scale url."""
        image = self._callFUT(self.data)
        self.assertEqual(
            image.get('tile'),
            'http://demo.com/pics/img1/@@scaling/img1-tile.jpeg',
        )

    def test_get_thumb(self):
        """Validate getting the 'thumb' scale url."""
        image = self._callFUT(self.data)
        self.assertEqual(
            image.get('thumb'),
            'http://demo.com/pics/img1/@@scaling/img1-thumb.jpeg',
        )

    def test_get_url(self):
        """Validate getting the 'url' scale url."""
        image = self._callFUT(self.data)
        self.assertEqual(
            image.get('url'),
            'http://demo.com/pics/img1/@@scaling/img1-url.jpeg',
        )

    def test_get_preview(self):
        """Validate getting the 'preview' scale url."""
        image = self._callFUT(self.data)
        self.assertEqual(
            image.get('preview'),
            'http://demo.com/pics/img1/@@scaling/img1-preview.jpeg',
        )

    def test_get_invalid(self):
        """Validate getting a non-existent scale url."""
        image = self._callFUT(self.data)
        self.assertIsNone(image.get('invalid'))

    def test_get_scale_title(self):
        """Validate the behavior of trying to get the 'title' scale url."""
        image = self._callFUT(self.data)
        self.assertIsNone(image.get('title'))

    def test_get_scale_id(self):
        """Validate the behavior of trying to get the 'id' scale url."""
        image = self._callFUT(self.data)
        self.assertIsNone(image.get('id'))

    def test_get_scale_description(self):
        """Validate the behavior of trying to get the 'description' scale url.
        """
        image = self._callFUT(self.data)
        self.assertIsNone(image.get('description'))
