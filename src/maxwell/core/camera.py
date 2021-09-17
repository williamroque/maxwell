import numpy as np


class Camera:
    "Operates on top of coordinate system."

    def __init__(self, client, factor=None, offset=None, center=None):
        if factor is None:
            factor = np.array([1, 1])

        if offset is None:
            offset = np.array([0, 0])

        if center is None:
            center = client.get_shape() / 2

        self.factor = factor
        self.offset = offset
        self.center = center

        self.hooks = []


    def pan(self, offset):
        self.offset = np.array(offset)


    def zoom(self, factor):
        self.factor = np.array(factor)


    def focus(self, center):
        self.center = np.array(center)


    def add_hook(self, hook, *arguments):
        self.hooks.append((hook, arguments))


    def run_hooks(self, scene):
        for hook, arguments in self.hooks:
            hook(scene, *arguments)


    def normalize(self, obj):
        return (np.array(obj) - self.center)*self.factor + self.offset + self.center


    def apply(self, shape, shape_props):
        keys = shape.properties.normalized_keys
        normalized = { key: self.normalize(shape_props[key]) for key in keys }

        return shape_props | normalized
