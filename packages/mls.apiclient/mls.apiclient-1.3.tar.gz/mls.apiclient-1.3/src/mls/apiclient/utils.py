# -*- coding: utf-8 -*-

# python imports
import urlparse
import re

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


def join_url(url, *paths):
    """Joins individual URL strings together, and returns a single string.

    Usage::

        >>> join_url('example.com', 'index.html')
        'example.com/index.html'
    """
    for path in paths:
        url = re.sub(r'/?$', re.sub(r'^/?', '/', path), url)
    return url


def join_url_params(url, params):
    """Constructs percent-encoded query string from given params dictionary.

    The result is appended to the given url.

    Usage::

        >>> join_url_params('example.com/index', {"count": 5, "type": "rl"})
        example.com/index?count=5&type=rl
    """
    return url + '?' + urlencode(params)


def merge_dict(data, *override):
    """Merges any number of dictionaries together.

    The result is a single dictionary.

    Usage::

        >>> merge_dict ({"foo": "bar"}, {1: 2}, {"count": 5})
        {1: 2, 'foo': 'bar', 'count': 5}
    """
    result = {}
    for current_dict in (data,) + override:
        result.update(current_dict)
    return result


def get_link(links, name):
    """Returns a specific link from a list of links with the given format:

    Usage::

        >>> links = [
        ...     {
        ...         "href" : "http://demomls.com",
        ...         "rel" : "self",
        ...     },
        ...     {
        ...         "href" : "http://demomls.com/next",
        ...         "rel" : "next",
        ...     },
        ... ]
        >>> get_link(links, 'self')
        http://demomls.com
        >>> get_link(links, 'next')
        http://demomls.com/next
    """
    if links is None:
        return None
    for link in links:
        if link.get('rel') == name:
            return link.get('href')


def split_url_params(url):
    """Split a url with parameters to return a tuple of the base url and a
    dictionary of the parameters.

    Usage::

        >>> split_url_params('http://demomls.com?param1=value1&param2=value2')
        ('http://demomls.com', {'param1': 'value1', 'param2': 'value2'})
    """
    params = {}
    parsed = url.split('?')
    base_url = parsed[0]
    if len(parsed) > 0:
        result = urlparse.urlparse(url)
        params = dict(urlparse.parse_qsl(result.query))
    return (base_url, params)


def extract_headers(headers, prefix):
    """Extract HTTP headers with the specific prefix from the HTTP response
    and return them in a dict.
    """
    prefix = prefix.upper() + '-'
    return dict((key[len(prefix):], val)
                for key, val in headers.items()
                if key.upper().startswith(prefix))


def wrap_data_response(data, status=200, headers={}):
    """Wrap a data dictionary with the appropriate response format if the
    response uses enveloped headers with optional parameters to include a
    specific status code and/or headers.
    """
    return {
        'status': status,
        'headers': headers,
        'response': data,
    }
