from m2x.v2.resource import Resource

# Wrapper for AT&T M2X Data Streams API
# https://m2x.att.com/developer/documentation/v2/device
class Stream(Resource):
    ITEM_PATH = 'devices/{device_id}/streams/{name}'
    COLLECTION_PATH = 'devices/{device_id}/streams'
    ITEMS_KEY = 'streams'
    ID_KEY = 'name'

    def __init__(self, api, device, **data):
        self.device = device
        super(Stream, self).__init__(api, **data)

    def update(self, **attrs):
        self.data.update(self.item_update(self.api, self.device, self.name, **attrs))
        return self.data

    def remove(self):
        return self.api.delete(self.subpath(""))

    def values(self, **params):
        return self.api.get(self.subpath('/values'), params=params)

    def sampling(self, interval, **params):
        params['interval'] = interval
        return self.api.get(self.subpath('/sampling'), params=params)

    def stats(self, **attrs):
        return self.api.get(self.subpath('/stats'), data=attrs)

    def add_value(self, value, timestamp=None):
        data = {'value': value}
        if timestamp:
            data['timestamp'] = timestamp
        return self.api.put(self.subpath('/value'), data=data)

    update_value = add_value

    def post_values(self, values):
        return self.api.post(self.subpath('/values'), data={
            'values': values
        })

    def delete_values(self, start, stop):
        return self.api.delete(self.subpath('/values'), data=self.to_server({
            'from': start,
            'end': stop
        }))

    def subpath(self, path):
        return self.item_path(self.name, device_id=self.device.id) + path

    @classmethod
    def list(cls, api, device, **params):
        # Search parameters: query, tags, page, limit
        path = cls.collection_path(device_id=device.id)
        return super(cls, cls).list(api, path=path, itemize_options={
            'device': device
        }, **params)

    @classmethod
    def create(cls, api, device, name, **attrs):
        response = cls.item_update(api, device, name, **attrs)
        return cls.item(api, response, device=device)

    @classmethod
    def get(cls, api, device, id, **params):
        path = cls.item_path(id, device_id=device.id)
        return super(cls, cls).get(api, id, path=path, itemize_options={
            'device': device
        }, **params)

    fetch = get

    @classmethod
    def item_update(cls, api, device, id, **params):
        path = cls.item_path(id, device_id=device.id)
        return super(cls, cls).item_update(api, id, path=path, **params)
