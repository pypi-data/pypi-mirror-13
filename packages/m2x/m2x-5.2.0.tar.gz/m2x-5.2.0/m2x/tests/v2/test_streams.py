import json

import httpretty

from m2x.client import M2XClient
from m2x.v2.api import APIVersion2
from m2x.tests.v2.base import BaseTestCase


class TestStreams(BaseTestCase):
    @httpretty.activate
    def setup_class(self):
        device = self.DATA['streams']['device']
        stream = self.DATA['streams']['stream']
        httpretty.register_uri(
            httpretty.GET,
            device['url'],
            body=json.dumps(device['response']),
            content_type='application/json'
        )
        httpretty.register_uri(
            httpretty.GET,
            stream['url'],
            body=json.dumps(stream['response']),
            content_type='application/json'
        )
        self.client = M2XClient(key=self.TEST_KEY, api=APIVersion2)
        self.device = self.client.device('device1')
        self.stream = self.device.stream('stream1')

    def teardown_class(self):
        self.client = None
        self.device = None
        self.stream = None

    @BaseTestCase.request_case
    def test_values(self, **kwargs):
        out = self.stream.values()
        assert 'values' in out
        assert len(out['values']) == 1

    @BaseTestCase.request_case
    def test_sampling(self, params=None, **kwargs):
        out = self.stream.sampling(*params)
        assert 'values' in out
        assert 'interval' in out
        assert len(out['values']) == 1

    @BaseTestCase.request_case
    def test_stats(self, **kwargs):
        out = self.stream.stats()
        assert 'stats' in out
        assert 'count' in out['stats']
        assert 'max' in out['stats']
        assert 'min' in out['stats']
        assert 'avg' in out['stats']
        assert 'stddev' in out['stats']

    @BaseTestCase.request_case
    def test_add_value(self, **kwargs):
        out = self.stream.add_value(1)
        assert out['status'] == 'accepted'

    @BaseTestCase.request_case
    def test_post_values(self, params=None, **kwargs):
        out = self.stream.post_values(params)
        assert out['status'] == 'accepted'

    @BaseTestCase.request_case
    def test_delete_values(self, params=None, **kwargs):
        self.stream.delete_values(**params)
        assert self.client.last_response.status == 204
