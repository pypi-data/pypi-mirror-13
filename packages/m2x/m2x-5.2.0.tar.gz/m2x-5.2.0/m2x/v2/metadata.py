class Metadata(object):
  def __init__(self, api, **data):
      self.api = api

  # Read an object's metadata
  #
  # https://m2x.att.com/developer/documentation/v2/device#Read-Device-Metadata
  # https://m2x.att.com/developer/documentation/v2/distribution#Read-Distribution-Metadata
  # https://m2x.att.com/developer/documentation/v2/collections#Read-Collection-Metadata
  def read_metadata(self):
    return self.api.get(self.metadata_path())

  # Read a single field of an object's metadata
  #
  # https://m2x.att.com/developer/documentation/v2/device#Read-Device-Metadata-Field
  # https://m2x.att.com/developer/documentation/v2/distribution#Read-Distribution-Metadata-Field
  # https://m2x.att.com/developer/documentation/v2/collections#Read-Collection-Metadata-Field
  def read_metadata_field(self, field):
    return self.api.get(self.metadata_field_path(field))

  # Update an object's metadata
  #
  # https://m2x.att.com/developer/documentation/v2/device#Update-Device-Metadata
  # https://m2x.att.com/developer/documentation/v2/distribution#Update-Distribution-Metadata
  # https://m2x.att.com/developer/documentation/v2/collections#Update-Collection-Metadata
  def update_metadata(self, params):
    return self.api.put(self.metadata_path(), data=params)

  # Update a single field of an object's metadata
  #
  # https://m2x.att.com/developer/documentation/v2/device#Update-Device-Metadata-Field
  # https://m2x.att.com/developer/documentation/v2/distribution#Update-Distribution-Metadata-Field
  # https://m2x.att.com/developer/documentation/v2/collections#Update-Collection-Metadata-Field
  def update_metadata_field(self, field, value):
    return self.api.put(self.metadata_field_path(field), data={ "value": value })

  def metadata_field_path(self, field):
    return '%s/%s' % (self.metadata_path(), field)

  def metadata_path(self):
    return self.subpath('/metadata')
