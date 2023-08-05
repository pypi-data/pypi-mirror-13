# -*- coding: utf-8 -*-

# python imports
import datetime
import json
import logging
import requests

# local imports
from mls.apiclient import HTTP_HEADER_PREFIX, PRODUCT_NAME
from mls.apiclient import exceptions, utils

logger = logging.getLogger(PRODUCT_NAME)


class API(object):
    """API class for the MLS.

    "The class contains all the base methods for establishing and
    authenticating the connections and requests to the MLS database.
    """

    def __init__(self, base_url, api_key=None, lang=None, debug=None):
        """Create API object.

        Usage::

            >>> from mls.apiclient import api
            >>> mls = api.API('http://demomls.com')
        """
        self.base_url = base_url
        self.api_key = api_key
        self.lang = lang
        self.debug = debug

    def request(self, url, method, body=None, params=None):
        """Make HTTP call, formats response and does error handling.
        Uses http_call method in API class.
        """

        url, url_params = utils.split_url_params(url)
        if params:
            url_params = utils.merge_dict(url_params, params)
        if self.api_key:
            url_params = utils.merge_dict(url_params, {'apikey': self.api_key})
        if self.lang:
            url_params = utils.merge_dict(url_params, {'lang': self.lang})
        url = utils.join_url_params(url, url_params)

        try:
            return self.http_call(
                url,
                method,
                data=json.dumps(body),
                headers=self.headers(),
            )
        except exceptions.BadRequest as error:
            # Format Error message for bad request
            return {'error': json.loads(error.content)}
        except requests.ConnectionError:
            raise exceptions.ServerError(503, url=url)

    def http_call(self, url, method, **kwargs):
        """Makes a http call. Logs response information."""

        if self.debug:
            logger.info('Request[{0}]: {1}'.format(method, url))
        start_time = datetime.datetime.now()

        response = requests.request(
            method,
            url,
            **kwargs
        )

        duration = datetime.datetime.now() - start_time
        if self.debug:
            logger.info('Response[{0}]: {1}, Duration: {2}.{3}s.'.format(
                response.status_code,
                response.reason,
                duration.seconds,
                duration.microseconds,
            ))

        return self.handle_response(response, response.content.decode('utf-8'))

    def handle_response(self, response, content):
        """Validate HTTP response."""

        def _validate_status_code(status_code, msg=None, url=None):
            if 200 <= status_code <= 299:
                return True
            elif status_code in (301, 302, 303, 307):
                raise exceptions.Redirection(status_code, msg, url)
            elif status_code == 400:
                raise exceptions.BadRequest(status_code, msg, url)
            elif status_code == 401:
                raise exceptions.UnauthorizedAccess(status_code, msg, url)
            elif status_code == 404:
                raise exceptions.ResourceNotFound(status_code, msg, url)
            elif 500 <= status_code <= 599:
                raise exceptions.ServerError(status_code, msg, url)
            else:
                raise exceptions.ConnectionError(status_code, msg, url)
            return False

        status = response.status_code
        msg = response.reason
        url = response.url
        if _validate_status_code(status, msg, url):
            data = json.loads(content) if content else {}
            status = data.get('status', None)
            if status is None:
                return utils.wrap_data_response(
                    data,
                    headers=utils.extract_headers(
                        response.headers,
                        HTTP_HEADER_PREFIX,
                    )
                )
            msg = data.get('response', '')
            if _validate_status_code(status, msg, url):
                return data

    def headers(self):
        """Default HTTP headers."""

        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

    def get(self, action, params=None):
        """Make GET request."""

        return self.request(
            utils.join_url(self.base_url, action),
            'GET',
            params=params or {},
        )
