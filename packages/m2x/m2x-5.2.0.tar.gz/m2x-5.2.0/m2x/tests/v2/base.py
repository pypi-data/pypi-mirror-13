import os
import json

from functools import wraps

import httpretty


DATA_FILE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    'data.json'
)


class BaseTestCase(object):
    TEST_KEY = 'foobar'
    DATA = json.loads(open(DATA_FILE, 'r').read())

    @classmethod
    def request_case(cls, func):
        @wraps(func)
        @httpretty.activate
        def wrapper(self):
            klass_name = self.__class__.__name__.lower()
            values = self.DATA[klass_name.replace('test', '')]
            values = values[func.__name__.replace('test_', '')]
            methods = {
                'GET': httpretty.GET,
                'POST': httpretty.POST,
                'PUT': httpretty.PUT,
                'OPTIONS': httpretty.OPTIONS,
                'DELETE': httpretty.DELETE
            }
            httpretty.register_uri(
                methods.get(values.get('method')) or httpretty.GET,
                values['url'],
                body=json.dumps(values['response']),
                content_type='application/json',
                status=values.get('status', 200)
            )
            func(self, **values)
        return wrapper
