from m2x.v2.api import APIVersion2


class M2XClient(object):
    ENDPOINT = 'https://api-m2x.att.com'

    def __init__(self, key, api=APIVersion2, endpoint=None, **kwargs):
        self.endpoint = endpoint or self.ENDPOINT
        self.api = api(key, self, **kwargs)

    def url(self, *parts):
        return '/'.join([part.strip('/') for part in (self.endpoint,) + parts
                         if part])

    def __getattr__(self, name):
        return getattr(self.api, name)
