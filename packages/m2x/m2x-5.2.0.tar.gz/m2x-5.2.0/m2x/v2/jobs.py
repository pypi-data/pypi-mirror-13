from m2x.v2.resource import Resource

# Wrapper for AT&T M2X Job API
# https://m2x.att.com/developer/documentation/v2/jobs
class Job(Resource):
    COLLECTION_PATH = 'jobs'
    ITEM_PATH = 'jobs/{id}'
    ITEMS_KEY = 'jobs'
