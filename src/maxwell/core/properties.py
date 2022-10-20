from json import dumps, JSONEncoder
from numpy import ndarray, isinf


class PropertiesEncoder(JSONEncoder):
    def default(self, obj):
        from maxwell.shapes.shape import Shape
        from maxwell.core.scene import Scene

        if isinstance(obj, ndarray):
            return obj.tolist()
        if isinstance(obj, (Shape, Scene)):
            out = {}

            if 'get_props' in dir(obj):
                out = obj.get_props()
            else:
                for k, v in obj.properties.__dict__.items():
                    if not k.startswith('_'):
                        out[k] = v

            return out

        return JSONEncoder.default(self, obj)


class Properties:
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]


    def __init__(self, **kwargs):
        self.normalized_keys = []

        for key, value in kwargs.items():
            setattr(self, key, value)


    def set_normalized(self, *normalized_keys):
        self.normalized_keys = normalized_keys


    def get_normalized(self, system):
        normalized = {}

        if system is not None:
            for obj in self.normalized_keys:
                if isinstance(obj, (tuple, ndarray, list)):
                    values = [getattr(self, key) for key in obj]
                    values = system.normalize(values).tolist()

                    for key, value in zip(obj, values):
                        normalized[key] = value
                else:
                    normalized[obj] = system.normalize(getattr(self, obj)).tolist()

        return { **self } | normalized
