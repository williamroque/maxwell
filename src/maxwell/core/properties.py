from json import dumps, JSONEncoder


class PropertiesEncoder(JSONEncoder):
    def default(self, obj):
        return {k: v for k, v in obj.properties.__dict__.items() if not k.startswith('_')}


class Properties:
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
