import numpy as np


class System:
    def __init__(self, client, scale, origin):
        self.client = client

        self.scale = np.array(scale)
        self.origin = np.array(origin)


    def set_origin(self, origin=None):
        if origin is not None:
            self.origin = np.array(origin)
        else:
            self.origin = self.client.get_shape() / 2


    def set_scale(self, scale):
        self.scale = np.array(scale)


    def scale_to_fit(self, curve, margin):
        quadrant_size = (self.client.get_shape() - margin) / 2
        max_point = np.amax(np.abs(curve), axis=0)

        self.scale = quadrant_size / max_point


    def normalize(self, obj):
        if isinstance(obj, (np.ndarray, list)):
            points = obj * self.scale * np.array([1, -1]) + self.origin
            return points

        if isinstance(obj, (int, float)):
            return obj * self.scale.sum()/2

        raise TypeError(f'Argument should be ndarray, list, or scalar. Type used: {type(points)}.')


    def from_normalized(self, points):
        points = (points - self.origin) / (self.scale * np.array([1, -1]))
        return points
