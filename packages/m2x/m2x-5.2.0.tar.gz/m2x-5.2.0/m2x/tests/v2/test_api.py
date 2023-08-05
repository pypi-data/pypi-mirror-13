import datetime

from m2x.client import M2XClient
from m2x.v2.api import APIVersion2
from m2x.tests.v2.base import BaseTestCase


class TestAPIVersion2(BaseTestCase):
    TEST_KEY = 'foobar'

    def setup_class(self):
        self.client = M2XClient(key=self.TEST_KEY, api=APIVersion2)
        self.api = self.client.api

    def teardown_class(self):
        self.client = None
        self.api = None

    @BaseTestCase.request_case
    def test_status(self, **kwargs):
        response = self.api.status()
        assert response['api'] == 'OK'
        assert response['triggers'] == 'OK'

    @BaseTestCase.request_case
    def test_device(self, params=None, **kwargs):
        out = self.api.device(*params)
        assert out.id == 'device1'
        assert out.status == 'enabled'
        assert out.name == 'Device1'
        assert out.tags is None
        assert out.url.endswith('device1')
        assert out.distribution == \
            'http://api-m2x.att.com/v2/distributions/distribution1'
        assert out.visibility == 'public'
        assert out.distribution_name == 'Distribution1'
        assert out.description == 'Device1'
        assert isinstance(out.last_activity, datetime.datetime)
        assert isinstance(out.created, datetime.datetime)
        assert isinstance(out.updated, datetime.datetime)

    @BaseTestCase.request_case
    def test_create_device(self, params=None, **kwargs):
        out = self.api.create_device(**params)
        assert out.id == 'device2'
        assert out.status == 'enabled'
        assert out.name == 'foobar'
        assert out.tags is None
        assert out.url.endswith('device2')
        assert out.visibility == 'public'
        assert out.serial is None
        assert out.description is None
        assert isinstance(out.last_activity, datetime.datetime)
        assert isinstance(out.created, datetime.datetime)
        assert isinstance(out.updated, datetime.datetime)

    @BaseTestCase.request_case
    def test_devices(self, **kwargs):
        out = self.api.devices()
        assert len(out) == 2
        assert set(['device2', 'device3']) == set([d.id for d in out])

    @BaseTestCase.request_case
    def test_device_catalog(self, **kwargs):
        out = self.api.device_catalog()
        assert len(out) == 2
        assert set(['device2', 'device3']) == set([d.id for d in out])

    @BaseTestCase.request_case
    def test_device_tags(self, **kwargs):
        out = self.api.device_tags()
        assert 'bar' in out
        assert 'foo' in out

    @BaseTestCase.request_case
    def test_distribution(self, params=None, **kwargs):
        out = self.api.distribution(*params)
        assert out.id == 'distribution1'
        assert out.url.endswith('distribution1')
        assert out.visibility == 'public'
        assert out.name == 'Distribution1'
        assert isinstance(out.created, datetime.datetime)
        assert isinstance(out.updated, datetime.datetime)

    @BaseTestCase.request_case
    def test_create_distribution(self, params=None, **kwargs):
        out = self.api.create_distribution(**params)
        assert out.id == 'distribution1'
        assert out.name == 'Distribution test'
        assert out.tags == []
        assert out.data['devices']['unregistered'] == 0
        assert out.data['devices']['registered'] == 0
        assert out.data['devices']['total'] == 0

    @BaseTestCase.request_case
    def test_distributions(self, **kwargs):
        out = self.api.distributions()
        assert len(out) == 2
        assert set([
            'distribution2',
            'distribution3'
        ]) == set([d.id for d in out])

    @BaseTestCase.request_case
    def test_key(self, params=None, **kwargs):
        out = self.api.key(*params)
        assert out.name == 'Key1'
        assert out.key == 'foobar'
        assert out.expired is False
        assert out.master is True

    @BaseTestCase.request_case
    def test_create_key(self, params=None, **kwargs):
        out = self.api.create_key(**params)
        assert out.name == 'Key2'
        assert out.key == 'abcdefg'
        assert out.expired is False
        assert out.master is True

    @BaseTestCase.request_case
    def test_keys(self, **kwargs):
        out = self.api.keys()
        assert len(out) == 2
        assert out[0].name == 'Key1'
        assert out[0].key == 'foobar'
        assert out[0].expired is False
        assert out[0].master is True
        assert out[1].name == 'Key2'
        assert out[1].key == 'abcdefg'
        assert out[1].expired is False
        assert out[1].master is True
