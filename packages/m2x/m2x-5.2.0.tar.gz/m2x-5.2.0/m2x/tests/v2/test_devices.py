import json

import httpretty

from m2x.client import M2XClient
from m2x.v2.api import APIVersion2
from m2x.v2.devices import Device
from m2x.tests.v2.base import BaseTestCase


class TestDevices(BaseTestCase):
    @httpretty.activate
    def setup_class(self):
        httpretty.register_uri(
            httpretty.GET,
            self.DATA['devices']['device']['url'],
            body=json.dumps(self.DATA['devices']['device']['response']),
            content_type='application/json'
        )
        self.client = M2XClient(key=self.TEST_KEY, api=APIVersion2)
        self.device = self.client.device(id='device1')

    def teardown_class(self):
        self.client = None
        self.device = None

    @BaseTestCase.request_case
    def test_streams(self, **kwargs):
        out = self.device.streams()
        assert len(out) == 1
        assert out[0].name == 'foobar'
        assert out[0].url.endswith('device1/streams/foobar')

    @BaseTestCase.request_case
    def test_create_stream(self, params=None, **kwargs):
        out = self.device.create_stream('stream1')
        assert out.name == 'stream1'
        assert out.url.endswith('device1/streams/stream1')

    @BaseTestCase.request_case
    def test_update_stream(self, params=None, **kwargs):
        out = self.device.update_stream('stream1', **params)
        assert out['unit']['label'] == 'Celsius'
        assert out['unit']['symbol'] == 'C'

    @BaseTestCase.request_case
    def test_keys(self, **kwargs):
        out = self.device.keys()
        assert len(out) == 1
        assert out[0].device.endswith(self.device.id)
        assert 'GET' in out[0].permissions
        assert 'POST' in out[0].permissions
        assert 'PUT' in out[0].permissions
        assert 'DELETE' in out[0].permissions

    @BaseTestCase.request_case
    def test_create_key(self, params=None, **kwargs):
        out = self.device.create_key(**params)
        assert out.device_access == "public"
        assert out.device.endswith(self.device.id)
        assert out.permissions == ["GET"]

    @BaseTestCase.request_case
    def test_location(self, **kwargs):
        out = self.device.location()
        assert out['latitude'] == '-32.8836'
        assert out['longitude'] == '-56.1819'

    @BaseTestCase.request_case
    def test_update_location(self, params=None, **kwargs):
        out = self.device.update_location(**params)
        assert out['status'] == 'accepted'

    @BaseTestCase.request_case
    def test_log(self, **kwargs):
        out = self.device.log()
        assert len(out['requests']) == 3

    @BaseTestCase.request_case
    def test_post_updates(self, params=None, **kwargs):
        out = self.device.post_updates(**params)
        assert out['status'] == 'accepted'

    @BaseTestCase.request_case
    def test_by_tags(self, **kwargs):
        out = Device.by_tags(self.client.api)
        assert out['foo'] == 1
        assert out['bar'] == 1

    @BaseTestCase.request_case
    def test_catalog(self, **kwargs):
        out = Device.catalog(self.client.api)
        assert len(out) == 2
