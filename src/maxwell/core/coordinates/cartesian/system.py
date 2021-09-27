"A cartesian coordinate system."

import numpy as np

from maxwell.core.coordinates.system import System


class CartesianSystem(System):
    "The cartesian coordinate system"

    def scale_to_fit(self, curve, margin):
        "Scale the coordinate system to fit a curve + margin."

        quadrant_size = self.client.get_shape() / 2 - margin
        max_point = np.amax(np.abs(curve), axis=0)

        self.scale = quadrant_size / max_point


    def normalize(self, obj):
        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)

            points = obj * self.scale * np.array([1, -1]) + self.origin
            return points
        elif isinstance(obj, (int, float)):
            return obj * self.scale.sum()/2

        raise TypeError(f'Argument should be ndarray, list, tuple, or scalar. Type used: {type(obj)}.')


    def from_normalized(self, obj):
        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)

            points = (obj - self.origin) / (self.scale * np.array([1, -1]))
            return points
        elif isinstance(obj, (int, float)):
            return obj / (self.scale.sum()/2)

        raise TypeError(f'Argument should be ndarray, list, tuple, or scalar. Type used: {type(points)}.')
