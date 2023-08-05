from m2x.client import M2XClient


TEST_KEY = 'foobar'


class TestM2XClient(object):
    def setup_class(self):
        self.client = M2XClient(key=TEST_KEY)

    def teardown_class(self):
        self.client = None

    def test_url(self):
        assert self.client.url('foo', 'bar') == M2XClient.ENDPOINT + '/foo/bar'
