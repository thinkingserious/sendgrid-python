import os
try:
    import unittest2 as unittest
except ImportError:
    import unittest
import json
import sys
try:
    from StringIO import StringIO
except ImportError:  # Python 3
    from io import StringIO
try:
    import urllib.request as urllib_request
    from urllib.parse import urlencode
    from urllib.error import HTTPError
except ImportError:  # Python 2
    import urllib2 as urllib_request
    from urllib2 import HTTPError
    from urllib import urlencode

import sendgrid
from sendgrid import SendGridClient, Mail
from sendgrid.exceptions import SendGridClientError, SendGridServerError
from sendgrid.sendgrid import HTTPError
from sendgrid.client import SendGridAPIClient
from sendgrid.version import __version__

SG_KEY  = os.getenv('SG_KEY') or 'SENDGRID_APIKEY'

class MockSendGridAPIClientRequest(SendGridAPIClient):
    def __init__(self, apikey, **opts):
        super(MockSendGridAPIClientRequest, self).__init__(apikey, **opts)
        self._req = None
        
    def _build_request(self, url=None, json_header=False, method='GET', data=None):
        req = urllib_request.Request(url)
        req.get_method = lambda: method
        req.add_header('User-Agent', self.useragent)
        req.add_header('Authorization', 'Bearer ' + self.apikey)
        if json_header:
            req.add_header('Content-Type', 'application/json')
        body = data
        if method == 'POST':
            response = 201
        if method == 'PATCH':
            response = 200
        if method == 'DELETE':
            response = 204
        if method == 'GET':
            response = 200
        return response, body

class TestSendGridAPIClient(unittest.TestCase):
    def setUp(self):
        self.client = MockSendGridAPIClientRequest
        self.client = SendGridAPIClient(SG_KEY)

    def test_apikey_init(self):
        self.assertEqual(self.client.apikey, SG_KEY)

    def test_useragent(self):
        useragent = 'sendgrid/' + __version__ + ';python_v3'
        self.assertEqual(self.client.useragent, useragent)

    def test_host(self):
        host = 'https://api.sendgrid.com'
        self.assertEqual(self.client.host, host)

class TestASMGroups(unittest.TestCase):
    def setUp(self):
        SendGridAPIClient = MockSendGridAPIClientRequest
        self.client = SendGridAPIClient(SG_KEY)
        
    def test_apikeys_init(self):
        self.asm_groups = self.client.asm_groups
        self.assertEqual(self.asm_groups.base_endpoint, "/v3/asm/groups")
        self.assertEqual(self.asm_groups.endpoint, "/v3/asm/groups")
        self.assertEqual(self.asm_groups.client, self.client)

    def test_asm_groups_get(self):
        status, msg = self.client.apikeys.get()
        self.assertEqual(status, 200)

if __name__ == '__main__':
    unittest.main()