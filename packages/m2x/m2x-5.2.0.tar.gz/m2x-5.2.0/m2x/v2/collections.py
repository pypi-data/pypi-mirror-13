from m2x.v2.resource import Resource
from m2x.v2.metadata import Metadata

# Wrapper for AT&T M2X Collections API
# https://m2x.att.com/developer/documentation/v2/collections
class Collection(Resource, Metadata):
    COLLECTION_PATH = 'collections'
    ITEM_PATH = 'collections/{id}'
    ITEMS_KEY = 'collections'
