# -*- coding: utf-8 -*-
"""mls.apiclient exception classes."""


class MLSError(Exception):
    """Main exception class."""
    pass


class ImproperlyConfigured(MLSError):
    """This exception is raised on configuration errors."""
    pass


class ObjectNotFound(MLSError):
    """This exception is raised if an object can not be found."""
    pass


class MultipleResults(MLSError):
    """This exception is raised on multiple results.

    That is, if a get request returns more than one result.
    """
    def __str__(self):
        return 'Your query had multiple results.'


class MissingParam(TypeError):
    pass


class ConnectionError(Exception):
    """Base exception for any type of connection error with the requests."""

    def __init__(self, status_code, reason=None, url=None):
        self.status_code = status_code
        self.reason = reason
        self.url = url

    def __str__(self):
        message = 'Response status: {0}.'.format(self.status_code)
        if self.reason:
            message += ' Reason: {0}.'.format(self.reason)
        if self.url:
            message += ' URL: {0}'.format(self.url)
        return message


class Redirection(ConnectionError):
    """3xx Redirection."""
    pass


class ClientError(ConnectionError):
    """4xx Client Error."""
    pass


class BadRequest(ClientError):
    """400 Bad Request."""
    pass


class UnauthorizedAccess(ClientError):
    """401 Unauthorized."""
    pass


class ResourceNotFound(ClientError):
    """404 Not Found."""
    pass


class ServerError(ConnectionError):
    """5xx Server Error."""
    pass
