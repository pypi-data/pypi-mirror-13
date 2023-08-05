from m2x.api import HTTPAPIBase
from m2x.v2.collections import Collection
from m2x.v2.commands import Command
from m2x.v2.devices import Device
from m2x.v2.distributions import Distribution
from m2x.v2.jobs import Job
from m2x.v2.keys import Key


class V2Mixin(object):
    PATH = '/v2'

    def status(self):
        return self.get('/status')

    def collection(self, id):
        return Collection.get(self, id)

    def create_collection(self, **params):
        return Collection.create(self, **params)

    def collections(self, **params):
        return Collection.list(self, **params)

    def command(self, id):
        return Command.get(self, id)

    def send_command(self, **params):
        return Command.create(self, **params)

    def commands(self, **params):
        return Command.list(self, **params)

    def device(self, id):
        return Device.get(self, id)

    def create_device(self, **params):
        return Device.create(self, **params)

    def devices(self, **params):
        return Device.list(self, **params)

    def devices_search(self, **params):
        return Device.search(self, **params)

    def device_catalog(self, **params):
        return Device.catalog(self, **params)

    def device_tags(self, **params):
        return Device.by_tags(self, **params)

    def distribution(self, id):
        return Distribution.get(self, id)

    def create_distribution(self, **params):
        return Distribution.create(self, **params)

    def distributions(self, **params):
        return Distribution.list(self, **params)

    def job(self, id):
        return Job.get(self, id)

    def key(self, key):
        return Key.get(self, key)

    def create_key(self, **params):
        return Key.create(self, **params)

    def keys(self, **params):
        return Key.list(self, **params)

    def time(self):
        return self.get('/time')

    def time_seconds(self):
        return self.get('/time/seconds')

    def time_millis(self):
        return self.get('/time/millis')

    def time_iso8601(self):
        return self.get('/time/iso8601').content


class APIVersion2(V2Mixin, HTTPAPIBase):
    pass
