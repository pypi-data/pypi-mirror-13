import json

import httpretty

from m2x.client import M2XClient
from m2x.v2.api import APIVersion2
from m2x.tests.v2.base import BaseTestCase


class TestDistributions(BaseTestCase):
    @httpretty.activate
    def setup_class(self):
        data = self.DATA['distributions']['distribution']
        httpretty.register_uri(
            httpretty.GET,
            data['url'],
            body=json.dumps(data['response']),
            content_type='application/json'
        )
        self.client = M2XClient(key=self.TEST_KEY, api=APIVersion2)
        self.distribution = self.client.distribution(id='distribution1')

    def teardown_class(self):
        self.client = None
        self.distribution = None

    @BaseTestCase.request_case
    def test_devices(self, **kwargs):
        out = self.distribution.devices()
        assert len(out) == 1
        assert out[0].id == 'device1'

    @BaseTestCase.request_case
    def test_add_device(self, params=None, **kwargs):
        out = self.distribution.add_device(**params)
        assert out.name == 'device3'
