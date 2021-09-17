import datetime
import colorsys

import numpy as np

from maxwell.shapes.line import Curve, LineSetProperties
from maxwell.shapes.arc import Arc
from maxwell.core.group import Group


class Vector(Curve):
    "Vector shape."

    def __init__(self, client, components, origin=None, shape_name=None, color='#fff', width=3, arrow_size=6, system=None, group=None):
        "This is a Curve wrapper for vectors."

        self.client = client
        self.system = system
        self.group = group

        if origin is None:
            origin = [0, 0]

        origin = list(origin)
        components = list(components)

        endpoint = [
            origin[0] + components[0],
            origin[1] + components[1]
        ]

        points = [origin, endpoint]

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        self.shape_name = shape_name

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        self.properties = LineSetProperties(
            type      = 'lineset',
            points    = points,
            color     = color,
            width     = width,
            arrows    = 1,
            arrowSize = arrow_size
        )


    @property
    def components(self):
        return self.properties.points[1]


    @property
    def origin(self):
        return self.properties.points[0]


    @components.setter
    def components(self, components):
        components = list(components)

        endpoint = [
            self.origin[0] + components[0],
            self.origin[1] + components[1]
        ]

        self.properties.points[1] = endpoint


    @origin.setter
    def origin(self, origin):
        self.properties.points[0] = list(origin)


    def normalize(self):
        norm = np.linalg.norm(self.components)

        if norm != 0:
            self.components = self.components / norm


class Colorschemes:
    @staticmethod
    def ratio_to_hex(ratio):
        return hex(int(255 * ratio))[2:]


    @staticmethod
    def coolwarm(magnitude, max_value):
        ratio = magnitude / max_value

        return '#{:0>2}55{:0>2}'.format(
            Colorschemes.ratio_to_hex(ratio),
            Colorschemes.ratio_to_hex(1 - ratio)
        )


    @staticmethod
    def greyscale(magnitude, max_value):
        ratio = magnitude / max_value

        return '#{0:0>2}{0:0>2}{0:0>2}'.format(
            Colorschemes.ratio_to_hex(ratio)
        )


    @staticmethod
    def red_green_blue(magnitude, max_value):
        ratio = 1 - magnitude / max_value

        norm_rgb = colorsys.hsv_to_rgb(ratio, .7, .6)

        color = '#{:0>2}{:0>2}{:0>2}'.format(
            Colorschemes.ratio_to_hex(norm_rgb[0]),
            Colorschemes.ratio_to_hex(norm_rgb[1]),
            Colorschemes.ratio_to_hex(norm_rgb[2])
        )

        return color


def create_vector_field(client, f, x, y, arrow_scale=.3, width=2, arrow_size=2, cmap='cw', max_threshold=np.inf, normalize=True, system=None):
    xx, yy = np.meshgrid(x, y)

    vector_field = f(xx, yy)

    magnitudes = np.linalg.norm(vector_field, axis=2)
    vector_field[magnitudes == 0] = np.nan

    if normalize:
        vector_field /= magnitudes[:, :, np.newaxis]

    cmap_key = {
        'cw': Colorschemes.coolwarm,
        'gs': Colorschemes.greyscale,
        'rgb': Colorschemes.red_green_blue,
        'w': lambda *_: '#fff',
        'b': lambda *_: '#000'
    }
    colormap = cmap_key[cmap]

    max_magnitude = min(magnitudes.max(), max_threshold)

    field_group = Group(background=True)

    for i, row in enumerate(vector_field):
        for j, vector in enumerate(row):
            origin = np.array([x[j], y[i]])
            shape_name = f'vector-{i}'

            if any(np.isnan(vector)):
                vector_shape = Arc(
                    client,
                    *origin,
                    color = colormap(0, max_magnitude),
                    system = system
                )
            else:
                vector_shape = Vector(
                    client,
                    vector * arrow_scale,
                    origin,
                    color = colormap(magnitudes[i, j], max_magnitude),
                    arrow_size = arrow_size,
                    width = width,
                    shape_name = shape_name
                )

            field_group.add_shape(vector_shape)

    return field_group
