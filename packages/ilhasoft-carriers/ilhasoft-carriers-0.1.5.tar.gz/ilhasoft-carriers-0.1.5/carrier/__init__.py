import json
from data import data


class Carrier(object):
    def __init__(self):
        self.data = data

    def get_query(self, field_object, field_search):
        return [obj for obj in self.data if obj[field_object] == str(field_search).lower()]

    def get_search(self, field, value):
        assert field.__class__.__name__ == 'str', '%s must be of type string' % field
        assert value.__class__.__name__ == 'str', '%s must be of type string' % value
        objects = self.get_query(field, value)
        return json.dumps(objects)
