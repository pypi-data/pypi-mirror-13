import sys
import json
import platform
import threading

from requests import session

from m2x import version
from m2x.utils import DateTimeJSONEncoder


PYTHON_VERSION = '{major}.{minor}.{micro}'.format(
    major=sys.version_info[0],
    minor=sys.version_info[1],
    micro=sys.version_info[2]
)

USER_AGENT = 'M2X-Python/{version} python/{python_version} ({platform})'\
    .format(version=version,
            python_version=PYTHON_VERSION,
            platform=platform.platform())


class APIBase(object):
    PATH = '/'

    def __init__(self, key, client, **kwargs):
        self.apikey = key
        self.client = client
        self._locals = threading.local()

    def url(self, *parts):
        parts = (self.client_endpoint(), self.PATH) + parts
        return '/'.join(map(lambda p: p.strip('/'), filter(None, parts)))

    def get(self, path, **kwargs):
        return self.request(path, **kwargs)

    def post(self, path, **kwargs):
        return self.request(path, method='POST', **kwargs)

    def put(self, path, **kwargs):
        return self.request(path, method='PUT', **kwargs)

    def delete(self, path, **kwargs):
        return self.request(path, method='DELETE', **kwargs)

    def patch(self, path, **kwargs):
        return self.request(path, method='PATCH', **kwargs)

    def head(self, path, **kwargs):
        return self.request(path, method='HEAD', **kwargs)

    def options(self, path, **kwargs):
        return self.request(path, method='OPTIONS', **kwargs)

    @property
    def last_response(self):
        return getattr(self._locals, 'last_response', None)

    @last_response.setter
    def last_response(self, value):
        self._locals.last_response = value

    def to_json(self, value):
        return json.dumps(value, cls=DateTimeJSONEncoder)

    def client_endpoint(self):
        raise NotImplementedError('Implement in subclass')

    def request(self, path, apikey=None, method='GET', **kwargs):
        raise NotImplementedError('Implement in subclass')


class Response(object):
    def __init__(self, response, raw, status, headers, json):
        self.response = response
        self.raw = raw
        self.status = status
        self.headers = headers
        self.json = json

    @property
    def success(self):
        return self.status >= 200 and self.status < 300

    @property
    def client_error(self):
        return self.status >= 400 and self.status < 500

    @property
    def server_error(self):
        return self.status >= 500

    @property
    def error(self):
        return self.client_error or self.server_error


class HTTPResponse(Response):
    def __init__(self, response):
        try:
            json = response.json()
        except ValueError:
            json = None
        super(HTTPResponse, self).__init__(
            response=response,
            raw=response.content,
            status=response.status_code,
            headers=response.headers,
            json=json
        )


class HTTPAPIBase(APIBase):
    @property
    def session(self):
        if not hasattr(self, '_session'):
            sess = session()
            sess.headers.update({'X-M2X-KEY': self.apikey,
                                 'Content-type': 'application/json',
                                 'Accept-Encoding': 'gzip, deflate',
                                 'User-Agent': USER_AGENT})
            self._session = sess
        return self._session

    def client_endpoint(self):
        return self.client.endpoint

    def request(self, path, apikey=None, method='GET', **kwargs):
        url = self.url(path)

        if apikey:
            kwargs.setdefault('headers', {})
            kwargs['headers']['X-M2X-KEY'] = apikey

        if method in ('PUT', 'POST', 'DELETE', 'PATCH') and kwargs.get('data'):
            kwargs['data'] = self.to_json(kwargs['data'])

        resp = self.session.request(method, url, **kwargs)
        self.last_response = HTTPResponse(resp)

        if resp.status_code == 204:
            return None
        else:
            resp.raise_for_status()
            try:
                return resp.json()
            except ValueError:
                return resp
