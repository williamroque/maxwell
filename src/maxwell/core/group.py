import numpy as np


class Group:
    def __init__(self, shapes={}):
        self.shapes = shapes

    def add_shape(self, obj, shape_id):
        if isinstance(obj, (list, tuple, np.ndarray)):
            for i, shape in enumerate(obj):
                self.shapes[f'{shape_id}-{i}'] = shape
        else:
            self.shapes[shape_id] = obj

    def render(self):
        for shape in self.shapes.values():
            shape.render()
