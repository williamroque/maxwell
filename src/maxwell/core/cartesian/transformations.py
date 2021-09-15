import numpy as np

from maxwell.shapes.line import Curve
from maxwell.core.group import Group

import colorsys


class System():
    def __init__(self, client, scale, origin):
        self.client = client

        self.scale = np.array(scale).astype(float)
        self.origin = np.array(origin).astype(float)

    def unset(self):
        self.origin = np.array([0, 0])
        self.scale = np.array([1, -1])

    def set_origin(self, origin=None):
        if origin is not None:
            self.origin = origin
        else:
            self.origin = self.client.get_shape() / 2

    def set_scale(self, scale):
        self.scale = scale

    def set_fill_scale(self, points, margin):
        self.scale = (self.client.get_shape() - margin) / 2 / np.amax(np.abs(points), axis=0)

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

    def zip_normalize(self, X, Y):
        return self.normalize(np.dstack((X, Y))[0])

    def zip_normalize_fill(self, X, Y, shape, margin):
        points = np.dstack((X, Y))[0]
        self.set_fill_scale(points, shape, margin)
        return self.normalize(points)

    def ratio_to_hex(self, ratio):
        return hex(int(255 * ratio))[2:]

    def coolwarm(self, magnitude, max_value):
        ratio = magnitude / max_value

        return '#{:0>2}55{:0>2}'.format(
            self.ratio_to_hex(ratio),
            self.ratio_to_hex(1 - ratio)
        )

    def greyscale(self, magnitude, max_value):
        ratio = magnitude / max_value

        return '#{0:0>2}{0:0>2}{0:0>2}'.format(
            self.ratio_to_hex(ratio)
        )

    def red_green_blue(self, magnitude, max_value):
        ratio = 1 - magnitude / max_value

        norm_rgb = colorsys.hsv_to_rgb(ratio, .7, .6)

        color = '#{:0>2}{:0>2}{:0>2}'.format(
            self.ratio_to_hex(norm_rgb[0]),
            self.ratio_to_hex(norm_rgb[1]),
            self.ratio_to_hex(norm_rgb[2])
        )

        return color

    def normalize_vector(self, v):
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm

    def render_normalized_2d_vector_field(self, f, X, Y, arrow_scale=.3, width=2, arrow_size=2, cmap='cw', max_threshold=np.inf, asgroup=False):
        xx, yy = np.meshgrid(X, Y)
        xx = xx.flatten()
        yy = yy.flatten()

        vector_field = []

        for x, y in zip(xx, yy):
            vector_field.append(f(x, y))

        magnitudes = []
        max_magnitude = 0
        for vector in vector_field:
            norm = np.linalg.norm(vector)
            magnitudes.append(norm)

            if norm > 0:
                vector /= norm

            if norm > max_magnitude:
                max_magnitude = norm

        cmap_key = {
            'cw': self.coolwarm,
            'gs': self.greyscale,
            'rgb': self.red_green_blue,
            'w': lambda *_: '#fff',
            'b': lambda *_: '#000'
        }

        colormap = np.vectorize(cmap_key[cmap], excluded=[1])(magnitudes, min(max_magnitude, max_threshold))

        field_group = Group(background=True)
        for i, vector in enumerate(vector_field):
            starting_point = np.array([xx[i], yy[i]])
            ending_point = starting_point + vector * arrow_scale

            arrow = Curve(
                self.client,
                [
                    self.normalize(starting_point),
                    self.normalize(ending_point)
                ],
                colormap[i], width=width,
                arrows=1, arrow_size=arrow_size
            )

            field_group.add_shape(arrow, f'vector-{i}')

        if not asgroup:
            return field_group.shapes.values()
        return field_group
