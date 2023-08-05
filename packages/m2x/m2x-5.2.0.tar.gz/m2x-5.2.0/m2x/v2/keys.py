from m2x.v2.resource import Resource

# Wrapper for AT&T M2X Keys API
# https://m2x.att.com/developer/documentation/v2/keys
class Key(Resource):
    COLLECTION_PATH = 'keys'
    ITEM_PATH = 'keys/{key}'
    ITEMS_KEY = 'keys'
    ID_KEY = 'key'

    def regenerate(self):
        self.data.update(
            self.api.post(self.item_path(self.key) + '/regenerate')
        )
