"A cartesian coordinate system."

import numpy as np

from maxwell.core.coordinates.system import System
from maxwell.core.group import Group
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.shape import ShapeConfig


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


    def get_grid(self, step_x=1, step_y=1):
        shape_config = ShapeConfig(client=self.client, system=self)
        axis_config = CurveConfig(width=2, color='#474747')

        width, height = self.client.get_shape()
        left, top = self.from_normalized((0, 0))
        right, bottom = self.from_normalized((width, height))

        x_count = int(np.ceil((abs(left) + abs(right)) / step_y))
        y_count = int(np.ceil((abs(top) + abs(bottom)) / step_x))

        grid_group = Group()

        x_axis = Curve(
            [(left, 0), (right, 0)],
            curve_config=axis_config,
            shape_config=shape_config
        )
        grid_group.add_shape(x_axis, 'x-axis')

        y_axis = Curve(
            [(0, top), (0, bottom)],
            curve_config=axis_config,
            shape_config=shape_config
        )
        grid_group.add_shape(y_axis, 'y-axis')

        primary_config = CurveConfig(width=2, color='#4447')
        secondary_config = CurveConfig(width=1, color='#6664')

        primary_grid = Group()
        secondary_grid = Group()

        for i in range(-x_count, x_count + 1):
            x_secondary = Curve(
                [(left, (i - 1/2) * step_y), (right, (i - 1/2) * step_y)],
                curve_config=secondary_config,
                shape_config=shape_config
            )
            secondary_grid.add_shape(x_secondary, f'x-secondary-({i})')

            if i == 0:
                continue

            x_primary = Curve(
                [(left, i * step_y), (right, i * step_y)],
                curve_config=primary_config,
                shape_config=shape_config
            )
            primary_grid.add_shape(x_primary, f'x-primary-({i})')

        for i in range(-y_count, y_count + 1):
            y_secondary = Curve(
                [((i - 1/2) * step_x, top), ((i - 1/2) * step_x, bottom)],
                curve_config=secondary_config,
                shape_config=shape_config
            )
            secondary_grid.add_shape(y_secondary, f'y-secondary-({i})')

            if i == 0:
                continue

            y_primary = Curve(
                [(i * step_x, top), (i * step_x, bottom)],
                curve_config=primary_config,
                shape_config=shape_config
            )
            primary_grid.add_shape(y_primary, f'y-primary-({i})')

        grid_group.merge_with(primary_grid)
        grid_group.merge_with(secondary_grid)

        return grid_group
