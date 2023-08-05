import os

APP_DIR = os.path.dirname((os.path.abspath(__file__)))
FILE_NAME = 'data'
FILE_PATH = "{0}/{1}.json".format(APP_DIR, FILE_NAME)

import json


class Carrier(object):
    def __init__(self):
        self.file = open(FILE_PATH)
        self.data = json.load(self.file)

    def get_query(self, field_object, field_search):
        return [obj for obj in self.data if obj[field_object] == str(field_search).lower()]

    def get_search(self, field, value):
        assert field.__class__.__name__ == 'str', '%s must be of type string' % field
        assert value.__class__.__name__ == 'str', '%s must be of type string' % value
        objects = self.get_query(field, value)
        self.file.close()
        return json.dumps(objects)
