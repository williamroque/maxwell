import numpy as np


class Group():
    def __init__(self, shapes=None, background=False):
        self.shapes = {}

        if shapes is not None:
            for shape_id, shape in shapes.items():
                self.add_shape(shape, shape_id)

        self.background = background

    def add_shape(self, obj, shape_id):
        from maxwell.core.cartesian.shapes import Axes, Grid

        if isinstance(obj, (list, tuple, np.ndarray, Axes, Grid)):
            for i, shape in enumerate(obj):
                self.shapes[f'{shape_id}-{i}'] = shape
        else:
            self.shapes[shape_id] = obj

    def render(self):
        for shape in self.shapes.values():
            shape.render(background=self.background)
