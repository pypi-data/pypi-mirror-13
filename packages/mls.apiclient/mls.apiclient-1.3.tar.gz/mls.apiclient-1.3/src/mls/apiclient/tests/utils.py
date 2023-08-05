# -*- coding: utf-8 -*-
"""Several test utils."""

# python imports
import os


def get_url(base_url, endpoint):
    return '/'.join([
        base_url,
        endpoint,
    ])


def load_fixture(name):
    """Return a file-like fixture, just like urlopen would."""
    fixture = open(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'fixtures',
            name,
        ), 'r'
    )
    return fixture.read()


def wrap_content(content, status_code=200, headers={}):
    """Wrap string JSON content in the appropriate response format with the
    given status code and return the JSON response as a string.
    """
    return u'{{"status": {0}, "headers": {1}, "response": {2}}}'.format(
        status_code,
        headers,
        content,
    )
