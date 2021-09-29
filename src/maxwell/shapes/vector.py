import datetime
import colorsys

import numpy as np

from maxwell.shapes.shape import ShapeConfig
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.arc import Arc, ArcConfig
from maxwell.core.group import Group


class Vector(Curve):
    "Vector shape."

    def __init__(self, components, origin=None, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        "This is a Curve wrapper for vectors."

        if origin is None:
            origin = [0, 0]

        origin = list(origin)
        components = list(components)

        endpoint = [
            origin[0] + components[0],
            origin[1] + components[1]
        ]

        points = [origin, endpoint]

        if curve_config is None:
            curve_config = self.get_default('curve_config', CurveConfig)

        curve_config.arrows = 1

        super().__init__(points, curve_config, shape_config)


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
    """All the vector field colorschemes. Methods should take
    magnitude and cap and return color.
    """

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


def create_vector_field(f, x, y, arrow_scale=.3, cmap='cw', max_threshold=np.inf, normalize=True, curve_config: CurveConfig = None, arc_config: ArcConfig = None, shape_config: ShapeConfig = None):
    if curve_config is None:
        curve_config = CurveConfig()

    if shape_config is None:
        shape_config = ShapeConfig()

    xx, yy = np.meshgrid(x, y)

    vector_field = np.dstack((f(xx, yy)))

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
            vector_shape_config = ShapeConfig(
                shape_name = f'vector-{i}-{j}',
                client = shape_config.client,
                system = shape_config.system
            )

            if any(np.isnan(vector)):
                arc_config.color = colormap(0, max_magnitude)

                vector_shape = Arc(
                    origin,
                    arc_config = arc_config,
                    shape_config = vector_shape_config
                )
            else:
                curve_config.color = colormap(magnitudes[i, j], max_magnitude)

                vector_shape = Vector(
                    vector * arrow_scale,
                    origin,
                    shape_config = vector_shape_config,
                    curve_config = curve_config
                )

            field_group.add_shape(vector_shape)

    return field_group
