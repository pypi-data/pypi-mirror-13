import json

import httpretty

from m2x.client import M2XClient
from m2x.tests.v2.base import BaseTestCase


class TestKeys(BaseTestCase):
    @httpretty.activate
    def setup_class(self):
        data = self.DATA['keys']['key']
        httpretty.register_uri(
            httpretty.GET,
            data['url'],
            body=json.dumps(data['response']),
            content_type='application/json'
        )
        self.client = M2XClient(key=self.TEST_KEY)
        self.key = self.client.key('key1')

    def teardown_class(self):
        self.client = None
        self.key = None

    @BaseTestCase.request_case
    def test_regenerate(self, **kwargs):
        self.key.regenerate()
        assert self.key.key == 'key1-regenerated'
