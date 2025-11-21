"To set up coordinate systems."

import numpy as np


class System:
    "An superclass for coordinate systems."

    DEFAULT_CLIENT = None

    def __init__(self, client=None, scale=None, origin=None):
        self.client = client
        if self.client is None:
            if System.DEFAULT_CLIENT is None:
                raise ValueError("Client specification required. Consider setting DEFAULT_CLIENT.")

            self.client = System.DEFAULT_CLIENT

        if scale is None:
            scale = (80.0, 80.0)

        if origin is None:
            origin = self.client.get_shape() / 2

        self.scale = np.array(scale)
        self.origin = np.array(origin)


    def set_origin(self, origin=None):
        "Set origin."

        if origin is not None:
            self.origin = np.array(origin)
        else:
            self.origin = self.client.get_shape() / 2


    def set_scale(self, scale, relative=False):
        "Set scale."

        scale = np.array(scale)

        if relative:
            self.scale *= scale
        else:
            self.scale = scale


    def zoom(self, factor):
        "Set relative scale."

        self.set_scale(factor, True)


    def translate(self, factor):
        "Set relative origin."

        self.origin -= self.scale * np.array(factor) * np.array([1, -1])


    def normalize(self, obj):
        """This is where the magic happens. Coordinate systems should
        override this to convert arrays and scalars into the canvas'
        coordinate system.
        """

        return np.array(obj) if isinstance(obj, (np.ndarray, list, tuple)) else obj


    def from_normalized(self, obj):
        "The inverse process of the above."

        return np.array(obj) if isinstance(obj, (np.ndarray, list, tuple)) else obj


    def apply_offset(self, point, offset):
        point = np.array(point)
        offset = np.array(offset)

        return self.from_normalized(self.normalize(point) + offset)


    def get_grid(self):
        "Create grid and axes. Specific to coordinate system."

        raise NotImplementedError
