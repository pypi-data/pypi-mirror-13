from m2x.v2.resource import Resource
from m2x.v2.metadata import Metadata
from m2x.v2.streams import Stream
from m2x.v2.keys import Key

# Wrapper for AT&T M2X Device API
# https://m2x.att.com/developer/documentation/v2/device
class Device(Resource, Metadata):
    COLLECTION_PATH = 'devices'
    ITEM_PATH = 'devices/{id}'
    ITEMS_KEY = 'devices'

    def streams(self):
        return Stream.list(self.api, self)

    def stream(self, name):
        return Stream.get(self.api, self, name)

    def create_stream(self, name, **params):
        return Stream.create(self.api, self, name, **params)

    def update_stream(self, name, **params):
        return Stream.item_update(self.api, self, name, **params)

    def keys(self):
        return Key.list(self.api, device=self.id)

    def create_key(self, **params):
        return Key.create(self.api, device=self.id, **params)

    def location(self):
        return self.data.get('location') or \
            self.api.get(self.subpath('/location')) or {}

    def location_history(self, **params):
        return self.api.get(self.subpath('/location/waypoints'), params=params)

    def update_location(self, **params):
        return self.api.put(self.subpath('/location'), data=params)

    def log(self):
        return self.api.get(self.subpath('/log'))

    def post_updates(self, **values):
        return self.api.post(self.subpath('/updates'), data=values)

    def post_update(self, **values):
        return self.api.post(self.subpath('/update'), data=values)

    def values(self, **params):
        return self.api.get(self.subpath('/values'), params=params)

    def values_export(self, **params):
        self.api.get(self.subpath('/values/export.csv'), params=params)
        return self.api.last_response

    def values_search(self, **params):
        return self.api.post(self.subpath('/values/search'), data=params)

    def commands(self, **params):
        return self.api.get(self.subpath('/commands'), params=params)

    def command(self, id):
        return self.api.get(self.subpath('/commands/%s' % id))

    def process_command(self, id, **params):
        return self.api.post(self.subpath('/commands/%s/process' % id), data=params)

    def reject_command(self, id, **params):
        return self.api.post(self.subpath('/commands/%s/reject' % id), data=params)

    @classmethod
    def by_tags(cls, api):
        response = api.get('devices/tags') or {}
        return response.get('tags') or []

    @classmethod
    def catalog(cls, api, **params):
        response = api.get('devices/catalog', **params)
        return cls.itemize(api, response)

    @classmethod
    def search(cls, api, **params):
        response = api.post('devices/search', data=params)
        return cls.itemize(api, response)
