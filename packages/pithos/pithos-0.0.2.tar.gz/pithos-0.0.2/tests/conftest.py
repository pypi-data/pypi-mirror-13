from __future__ import unicode_literals

import logging

import pytest

from pithos import BaseSessionHandler

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture(scope='module')
def request_class():
    """ Returns request class
    """
    class Request(object):
        cookies = {}

    return Request


@pytest.fixture(scope='module')
def handler_class():
    """ Returns TestHandler class
    """
    class TestHandler(BaseSessionHandler):
        """ In test request and reponse objects are identical ;-)
        """
        def set_cookie(self, response, value):
            response.cookies[self.cookie_name] = {
                'domain': self.cookie_domain,
                'path': self.cookie_path,
                'httponly': self.cookie_httponly,
                'secure': self.cookie_secure,
                'value': value,
            }

        def get_cookie(self, request):
            cookie = request.cookies.get(self.cookie_name)
            if cookie:
                return cookie['value']

        def get_remote_ip(self, request):
            return '127.0.0.1'

    return TestHandler
