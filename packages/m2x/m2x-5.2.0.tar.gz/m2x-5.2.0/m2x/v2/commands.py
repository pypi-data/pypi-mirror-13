from m2x.v2.resource import Resource

# Wrapper for AT&T M2X Commands API
# https://m2x.att.com/developer/documentation/v2/commands
class Command(Resource):
    COLLECTION_PATH = 'commands'
    ITEM_PATH = 'commands/{id}'
    ITEMS_KEY = 'commands'
