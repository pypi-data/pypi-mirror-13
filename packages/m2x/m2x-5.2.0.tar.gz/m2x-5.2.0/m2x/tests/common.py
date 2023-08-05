from m2x.client import M2XClient
from m2x.api import APIBase, Response


class DummyResponse(Response):
    def __init__(self, response):
        super(DummyResponse, self).__init__(
            response=response,
            raw=response,
            status=response.status_code,
            headers=response.headers,
            json=response.json
        )


class _Response(object):
    def __init__(self, request):
        self.request = request
        self.url = request.url
        self.method = request.method
        self.apikey = request.apikey
        self.kwargs = request.kwargs
        self.status_code = 200
        self.headers = request.kwargs
        self.json = None


class DummyRequest(object):
    def __init__(self, url, method, apikey, **kwargs):
        self.url = url
        self.method = method
        self.apikey = apikey
        self.kwargs = kwargs

    def response(self):
        return _Response(self)


class DummyAPI(APIBase):
    PATH = '/dummy'

    def client_endpoint(self):
        return self.client.endpoint

    def request(self, path, apikey=None, method='GET', **kwargs):
        apikey = apikey or self.apikey
        request = DummyRequest(self.url(path), method, apikey, **kwargs)
        response = request.response()
        self.last_response = DummyResponse(response)
        return response


class DummyClient(M2XClient):
    ENDPOINT = 'http://api.m2x.com'

    def __init__(self, key, api=DummyAPI, endpoint=None, **kwargs):
        super(DummyClient, self).__init__(key, api, endpoint, **kwargs)
