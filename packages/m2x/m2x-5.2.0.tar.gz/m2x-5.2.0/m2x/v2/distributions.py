from m2x.v2.resource import Resource
from m2x.v2.metadata import Metadata
from m2x.v2.devices import Device

class DistributionDevice(Device):
    COLLECTION_PATH = 'distributions/{distribution_id}/devices'

# Wrapper for AT&T M2X Distribution API
# https://m2x.att.com/developer/documentation/v2/distribution
class Distribution(Resource, Metadata):
    COLLECTION_PATH = 'distributions'
    ITEM_PATH = 'distributions/{id}'
    ITEMS_KEY = 'distributions'

    def devices(self):
        return DistributionDevice.list(self.api, distribution_id=self.id)

    def add_device(self, serial):
        return DistributionDevice.create(self.api, distribution_id=self.id,
                                         serial=serial)
