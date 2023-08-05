import pytest

from m2x.api import APIBase
from m2x.client import M2XClient

from m2x.tests.common import DummyClient


TEST_KEY = 'foobar'


class TestAPIBase(object):
    def setup_class(self):
        self.client = M2XClient(key=TEST_KEY, api=APIBase)
        self.api = self.client.api

    def teardown_class(self):
        self.client = None
        self.api = None

    def test_url(self):
        with pytest.raises(NotImplementedError):
            self.api.url('foo', 'bar')

    def test_get(self):
        with pytest.raises(NotImplementedError):
            self.api.get('/get', foo='bar')

    def test_post(self):
        with pytest.raises(NotImplementedError):
            self.api.post('/post', foo='bar')

    def test_put(self):
        with pytest.raises(NotImplementedError):
            self.api.put('/put', foo='bar')

    def test_delete(self):
        with pytest.raises(NotImplementedError):
            self.api.delete('/delete', foo='bar')

    def test_patch(self):
        with pytest.raises(NotImplementedError):
            self.api.patch('/patch', foo='bar')

    def test_head(self):
        with pytest.raises(NotImplementedError):
            self.api.head('/head', foo='bar')

    def test_options(self):
        with pytest.raises(NotImplementedError):
            self.api.options('/options', foo='bar')

    def test_last_response(self):
        assert self.api.last_response is None

    def test_to_json(self):
        val = self.api.to_json({'foo': 'bar'})
        assert val == '{"foo": "bar"}'

    def test_client_endpoint(self):
        with pytest.raises(NotImplementedError):
            self.api.client_endpoint()

    def test_request(self):
        with pytest.raises(NotImplementedError):
            self.api.request('/req')


class TestDummyAPI(object):
    def setup_class(self):
        self.client = DummyClient(key=TEST_KEY)
        self.api = self.client.api

    def teardown_class(self):
        self.client = None
        self.api = None

    def test_url(self):
        assert self.api.url('foo', 'bar') == \
            self.client.ENDPOINT + '/dummy/foo/bar'
        assert self.api.url() == \
            self.client.ENDPOINT + '/dummy'

    def test_get(self):
        resp = self.api.get('/get', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/get'
        assert resp.method == 'GET'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'

    def test_post(self):
        resp = self.api.post('/post', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/post'
        assert resp.method == 'POST'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'

    def test_put(self):
        resp = self.api.put('/put', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/put'
        assert resp.method == 'PUT'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'

    def test_delete(self):
        resp = self.api.delete('/delete', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/delete'
        assert resp.method == 'DELETE'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'

    def test_patch(self):
        resp = self.api.patch('/patch', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/patch'
        assert resp.method == 'PATCH'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'

    def test_head(self):
        resp = self.api.head('/head', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/head'
        assert resp.method == 'HEAD'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'

    def test_options(self):
        resp = self.api.options('/options', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/options'
        assert resp.method == 'OPTIONS'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'

    def test_last_response(self):
        resp = self.api.get('/get', foo='bar')
        last_response = self.api.last_response
        assert last_response.raw == resp

    def test_to_json(self):
        val = self.api.to_json({'foo': 'bar'})
        assert val == '{"foo": "bar"}'

    def test_client_endpoint(self):
        self.api.client_endpoint() == self.client.ENDPOINT

    def test_request(self):
        resp = self.api.get('/get', foo='bar')
        assert resp.url == self.client.ENDPOINT + '/dummy/get'
        assert resp.method == 'GET'
        assert resp.apikey == TEST_KEY
        assert resp.kwargs['foo'] == 'bar'
