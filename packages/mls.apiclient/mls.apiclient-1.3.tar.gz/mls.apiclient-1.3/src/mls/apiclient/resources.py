# -*- coding: utf-8 -*-
"""MLS rest client entity resource classes."""

# python imports
import urlparse

# local imports
from mls.apiclient import (
    REST_API_URL,
    REST_API_VERSION,
    client,
    utils,
)

IMG_FIELDS = ('id', 'title', 'description', )


class Image(object):
    """Image resource."""

    def __init__(self, data):
        self._data = data

    @property
    def title(self):
        return self._data.get('title')

    @property
    def id(self):
        return self._data.get('id')

    @property
    def description(self):
        return self._data.get('description')

    def get(self, scale='url'):
        if scale in IMG_FIELDS:
            return
        return self._data.get(scale)


class Resource(object):
    """Base class for resources."""

    endpoint = None

    def __init__(self, api, data):
        if not isinstance(data, dict):
            raise ValueError(
                'Data must be dictionary with content of the resource.'
            )

        self._api = api
        self._headers = data.get('headers', {})
        self._data = data.get('response', {})
        self._links = self._data.get('links', {})

    def __getattr__(self, name):
        """Returns a data attribute or raises AttributeError."""
        try:
            return self._data[name]
        except KeyError:
            return object.__getattribute__(self, name)

    @classmethod
    def get(cls, api, resource_id):
        """Returns one object of this Resource.

        You have to give one keyword argument to find the object.
        """
        url = utils.join_url(cls.get_endpoint_url(), resource_id)
        return cls(api, api.get(url))

    @classmethod
    def search(cls, api, params=None):
        """Returns a list of objects with optional search parameters.

        You can search for objects by giving one or more keyword arguments.
        Use limit and offset to limit the results.
        """
        url = cls.get_endpoint_url()
        return cls(api, api.get(url, params))

    @classmethod
    def get_field_titles(cls, api):
        """Return the translated titles of the fields."""
        url = utils.join_url(
            REST_API_URL,
            REST_API_VERSION,
            'field_titles',
            cls.endpoint,
        )
        return api.get(url)

    @classmethod
    def get_field_order(cls, api):
        """Return the list of fieldnames in order as defined in the MLS."""
        url = utils.join_url(
            REST_API_URL,
            REST_API_VERSION,
            'field_order',
            cls.endpoint,
        )
        return api.get(url)

    @classmethod
    def get_endpoint_url(cls):
        """Returns the URL to the resource object."""
        return utils.join_url(REST_API_URL, REST_API_VERSION, cls.endpoint)

    def get_attributes(self):
        """Returns a list of all attributes of a Resource object."""
        return self._data.keys()

    def get_id(self):
        """Returns the id of the resource object."""
        return self._data.get('id', None)

    def get_url(self):
        """Returns the URL to the resource object."""
        return utils.get_link(self._links, 'self')

    def get_headers(self):
        """Returns a dictionary of the headers for this resource object."""
        return self._headers

    def get_items(self):
        """Returns the list of Resource objects when the data contains a
        collection.
        """
        result = []
        for item in self._data.get('collection', []):
            data = utils.wrap_data_response(item)
            result.append(self.__class__(self._api, data))
        return result

    def _return_value(self, fields, data):
        return dict([(
            f, {'label': fields.get(f, f), 'value': data.get(f, None)}
        ) for f in data.keys()])


class Agency(Resource):
    """'Agency' entity resource class."""

    endpoint = 'agencies'

    def listings(self, params=None):
        """Search for listings within that agency."""
        raise NotImplementedError

    def developments(self):
        """Search for developments within that agency."""
        raise NotImplementedError


class Agent(Resource):
    """'Agent' entity resource class."""

    endpoint = 'agents'

    def listings(self, params=None):
        """Search for listings for that agent."""
        raise NotImplementedError


class Development(Resource):
    """'Development Project' entity resource class."""

    endpoint = 'developments'

    def __init__(self, api, data):
        super(Development, self).__init__(api, data)
        self.__class_agency__ = Agency
        self.__class_agent__ = Agent
        self.__class_group__ = PropertyGroup
        self.__class_phase__ = DevelopmentPhase

    def agency(self):
        """Return the responsible agency for this development."""
        value = self._data.get('agency', None)
        if value is not None:
            data = {
                'response': value,
            }
            return self.__class_agency__(self._api, data)

    def agent(self):
        """Return the responsible agent for this development."""
        value = self._data.get('agent', None)
        if value is not None:
            data = {
                'response': value,
            }
            return self.__class_agent__(self._api, data)

    def groups(self, params=None):
        """Search for property groups within that development."""
        url = self._data.get('groups')
        data = self._api.request(url, 'GET', params=params)
        return self.__class_group__(self._api, data).get_items()

    def listings(self, params=None):
        """Search for listings assigned to that development project."""
        if params is None:
            params = {}
        url = self._data.get('listing_url', None)
        if url is None:
            return
        url_params = url.split('?')
        if len(url_params) < 2:
            return
        url_params = dict(urlparse.parse_qsl(url_params[1]))
        params.update(url_params)
        listing_resource = client.ListingResource(
            self._api.base_url, api_key=self._api.api_key,
        )
        return listing_resource.search(params=params)

    def phases(self, params=None):
        """Search for development phases within that development."""
        url = self._data.get('phases')
        data = self._api.request(url, 'GET', params=params)
        return self.__class_phase__(self._api, data).get_items()

    def pictures(self):
        """Get the pictures for that development."""
        result = []
        items = self._data.get('pictures', [])
        if items is None:
            return
        for item in items:
            result.append(Image(item))
        return result

    def representatives(self):
        """Get the representatives for that development."""
        result = []
        items = self._data.get('representatives', [])
        if items is None:
            return
        for item in items:
            data = {
                'response': item,
            }
            result.append(self.__class_agent__(self._api, data))
        return result


class DevelopmentPhase(Resource):
    """'Development Phase' entity resource class."""

    endpoint = 'development_phases'

    def listings(self, params=None):
        """Search for listings assigned to that development phase."""
        if params is None:
            params = {}
        url = self._data.get('listing_url', None)
        if url is None:
            return
        url_params = url.split('?')
        if len(url_params) < 2:
            return
        url_params = dict(urlparse.parse_qsl(url_params[1]))
        params.update(url_params)
        listing_resource = client.ListingResource(
            self._api.base_url, api_key=self._api.api_key,
        )
        return listing_resource.search(params=params)


class Listing(Resource):
    """'Listing' entity resource class."""

    def pictures(self):
        """Get the pictures for that listing."""
        raise NotImplementedError


class PropertyGroup(Resource):
    """'Property Group' entity resource class."""

    endpoint = 'property_groups'

    def listings(self, params=None):
        """Search for listings assigned to that property group."""
        if params is None:
            params = {}
        url = self._data.get('listing_url', None)
        if url is None:
            return
        url_params = url.split('?')
        if len(url_params) < 2:
            return
        url_params = dict(urlparse.parse_qsl(url_params[1]))
        params.update(url_params)
        listing_resource = client.ListingResource(
            self._api.base_url, api_key=self._api.api_key,
        )
        return listing_resource.search(params=params)
