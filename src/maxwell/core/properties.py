from json import dumps, JSONEncoder
from numpy import ndarray, int64, float64


class PropertiesEncoder(JSONEncoder):
    def default(self, obj):
        from maxwell.shapes.shape import Shape
        from maxwell.core.scene import Scene

        if isinstance(obj, ndarray):
            return obj.tolist()
        elif isinstance(obj, (Shape, Scene)):
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

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
