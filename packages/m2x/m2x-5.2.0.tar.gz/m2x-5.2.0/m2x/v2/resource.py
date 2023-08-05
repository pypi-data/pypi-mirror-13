from m2x.utils import attrs_to_server, attrs_from_server


class Resource(object):
    COLLECTION_PATH = ''
    ITEM_PATH = ''
    ID_KEY = 'id'
    ITEMS_KEY = None
    DEFAULT_LIMIT = 256

    def __init__(self, api, **data):
        self.api = api
        self.data = self.from_server(data)

    def update(self, **attrs):
        self.data.update(self.item_update(self.api, self.id, **attrs))
        return self.data

    def remove(self):
        return self.api.delete(self.item_path(self.id))

    def subpath(self, path):
        return self.item_path(self[self.ID_KEY]) + path

    @classmethod
    def list(cls, api, path=None, **params):
        # Search parameters: query, tags, page, limit
        itemize_options = params.pop('itemize_options', {})
        params = cls.to_server(params)
        response = api.get(path or cls.collection_path(**params),
                           params=params)
        return cls.itemize(api, response, **itemize_options)

    @classmethod
    def create(cls, api, path=None, **attrs):
        itemize_options = attrs.pop('itemize_options', {})
        data = cls.to_server(attrs)
        response = api.post(path or cls.collection_path(**attrs), data=data)
        return cls.item(api, response, **itemize_options)

    @classmethod
    def get(cls, api, id, path=None, **params):
        itemize_options = params.pop('itemize_options', {})
        response = api.get(path or cls.item_path(id, **params))
        return cls.item(api, response, **itemize_options)

    @classmethod
    def item_update(cls, api, id, path=None, **params):
        params = cls.to_server(params)
        path = path or cls.item_path(id, **params)
        response = api.put(path, data=params)
        return cls.from_server(response or params)

    @classmethod
    def item(cls, api, entry, **options):
        options.update(cls.from_server(entry))
        return cls(api, **options)

    @classmethod
    def itemize(cls, api, entries, **options):
        if cls.ITEMS_KEY and cls.ITEMS_KEY in entries:
            entries = [cls.item(api, entry, **options)
                       for entry in entries[cls.ITEMS_KEY]]
        return entries

    @classmethod
    def collection_path(self, **kwargs):
        return self.COLLECTION_PATH.format(**kwargs)

    @classmethod
    def item_path(cls, id, **kwargs):
        kwargs[cls.ID_KEY] = id
        return cls.ITEM_PATH.format(**kwargs)

    @classmethod
    def to_server(cls, values):
        return attrs_to_server(values)

    @classmethod
    def from_server(cls, values):
        return attrs_from_server(values)

    def __getattr__(self, name):
        try:
            return self.data[name]
        except KeyError as err:
            raise AttributeError('{0}'.format(err))

    def __getitem__(self, name):
        return self.data[name]
