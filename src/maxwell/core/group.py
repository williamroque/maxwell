import numpy as np


class Group():
    def __init__(self, shapes=None, background=False):
        self.shapes = {}

        if shapes is not None:
            for shape_id, shape in shapes.items():
                self.add_shape(shape, shape_id)

        self.background = background

    def add_shape(self, obj, shape_name=None):
        from maxwell.core.cartesian.shapes import Axes, Grid

        if isinstance(obj, (list, tuple, np.ndarray, Axes, Grid)):
            for i, shape in enumerate(obj):
                self.shapes[shape.shape_name] = shape
        else:
            if shape_name is None:
                self.shapes[shape.shape_name] = obj
            else:
                self.shapes[shape_name] = obj

    def render(self, exclude_shape=None):
        for shape in self.shapes.values():
            if exclude_shape is None or shape != exclude_shape:
                shape.render(background=self.background)

        return self
