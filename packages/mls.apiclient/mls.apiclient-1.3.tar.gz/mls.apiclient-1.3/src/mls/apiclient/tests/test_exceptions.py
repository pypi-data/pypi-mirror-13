# -*- coding: utf-8 -*-
"""Test custom exception classes."""

# python imports
from collections import namedtuple

# local imports
from mls.apiclient import exceptions
from mls.apiclient.tests import base


class TestExceptions(base.BaseTestCase):

    def setUp(self):
        self.Response = namedtuple('Response', 'status_code reason')

    def test_connection(self):
        error = exceptions.ConnectionError(
            400,
            reason='Bad request',
            url='http://demomls.com/request',
        )
        self.assertEqual(
            str(error),
            'Response status: 400. Reason: Bad request. '
            'URL: http://demomls.com/request',
        )

    def test_redirect(self):
        error = exceptions.Redirection(
            401,
            reason='Redirect => http://example.com',
        )
        self.assertEqual(
            str(error),
            'Response status: 401. Reason: Redirect => http://example.com.',
        )

    def test_not_found(self):
        response = self.Response(status_code='404', reason='Not Found')
        error = exceptions.ResourceNotFound(
            response.status_code,
            response.reason,
        )
        self.assertEqual(
            str(error),
            'Response status: {0}. Reason: {1}.'.format(
                response.status_code, response.reason,
            )
        )

    def test_unauthorized_access(self):
        response = self.Response(status_code='401', reason='Unauthorized')
        error = exceptions.UnauthorizedAccess(
            response.status_code,
            response.reason,
        )
        self.assertEqual(
            str(error),
            'Response status: {0}. Reason: {1}.'.format(
                response.status_code, response.reason,
            )
        )

    def test_missing_param(self):
        error = exceptions.MissingParam('Missing Payment Id')
        self.assertEqual(str(error), 'Missing Payment Id')

    def test_missing_config(self):
        error = exceptions.MissingParam('Missing client_id')
        self.assertEqual(str(error), 'Missing client_id')
