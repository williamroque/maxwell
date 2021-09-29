"A cartesian coordinate system."

from dataclasses import dataclass

from typing import Callable

import numpy as np

from maxwell.core.coordinates.system import System
from maxwell.core.group import Group
from maxwell.core.util import pi_format
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.shape import ShapeConfig
from maxwell.shapes.latex import Latex, LatexConfig


@dataclass
class CartesianGridConfig:
    step_x: float = 1
    step_y: float = 1
    show_numbers: bool = True
    label_config: LatexConfig = LatexConfig(color='#555', font_size=8)
    x_label_format: Callable = None
    y_label_format: Callable = None
    x_label_offset: tuple = (0, -20)
    y_label_offset: tuple = (-15, 15)


class CartesianSystem(System):
    "The cartesian coordinate system"

    def scale_to_fit(self, curve, margin):
        "Scale the coordinate system to fit a curve + margin."

        quadrant_size = self.client.get_shape() / 2 - margin
        max_point = np.amax(np.abs(curve), axis=0)

        self.scale = quadrant_size / max_point


    def plot(self, func, start, end, point_num=400, render=True, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        if shape_config is None:
            shape_config = ShapeConfig()

        shape_config.system = self

        x_values = np.linspace(start, end, point_num)
        y_values = func(x_values)

        curve = Curve(zip(x_values, y_values), curve_config, shape_config)

        if render:
            curve.render()

        return curve


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


    def get_grid(self, grid_config: CartesianGridConfig = None, render=True):
        if grid_config is None:
            grid_config = CartesianGridConfig()

        shape_config = ShapeConfig(client=self.client, system=self)
        axis_config = CurveConfig(width=2, color='#474747')

        width, height = self.client.get_shape()
        left, top = self.from_normalized((0, 0))
        right, bottom = self.from_normalized((width, height))

        x_label_offset = np.array(grid_config.x_label_offset)/self.scale
        y_label_offset = np.array(grid_config.y_label_offset)/self.scale

        x_count = int(np.ceil((abs(left) + abs(right)) / grid_config.step_y))
        y_count = int(np.ceil((abs(top) + abs(bottom)) / grid_config.step_x))

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
        x_labels = Group()
        y_labels = Group()

        for i in range(-x_count, x_count + 1):
            x_secondary = Curve(
                [(left, (i - 1/2) * grid_config.step_y), (right, (i - 1/2) * grid_config.step_y)],
                curve_config=secondary_config,
                shape_config=shape_config
            )
            secondary_grid.add_shape(x_secondary, f'x-secondary-({i})')

            if i == 0:
                continue

            x_primary = Curve(
                [(left, i * grid_config.step_y), (right, i * grid_config.step_y)],
                curve_config=primary_config,
                shape_config=shape_config
            )
            primary_grid.add_shape(x_primary, f'x-primary-({i})')

            if grid_config.show_numbers:
                if grid_config.y_label_format is None:
                    label = str(i * grid_config.step_y)
                else:
                    label = grid_config.y_label_format(i * grid_config.step_y)

                label_shape = Latex(
                    label,
                    np.array((0, i * grid_config.step_y)) + y_label_offset,
                    latex_config=grid_config.label_config,
                    shape_config=shape_config
                )

                y_labels.add_shape(label_shape, f'y-label-{i}')

        for i in range(-y_count, y_count + 1):
            y_secondary = Curve(
                [((i - 1/2) * grid_config.step_x, top), ((i - 1/2) * grid_config.step_x, bottom)],
                curve_config=secondary_config,
                shape_config=shape_config
            )
            secondary_grid.add_shape(y_secondary, f'y-secondary-({i})')

            if i == 0:
                continue

            y_primary = Curve(
                [(i * grid_config.step_x, top), (i * grid_config.step_x, bottom)],
                curve_config=primary_config,
                shape_config=shape_config
            )
            primary_grid.add_shape(y_primary, f'y-primary-({i})')

            if grid_config.show_numbers:
                if grid_config.x_label_format is None:
                    label = str(i * grid_config.step_x)
                else:
                    label = grid_config.x_label_format(i * grid_config.step_x)

                label_shape = Latex(
                    label,
                    np.array((i * grid_config.step_x, 0)) + x_label_offset,
                    latex_config=grid_config.label_config,
                    shape_config=shape_config
                )

                x_labels.add_shape(label_shape, f'x-label-{i}')

        grid_group.merge_with(primary_grid)
        grid_group.merge_with(secondary_grid)
        grid_group.merge_with(x_labels)
        grid_group.merge_with(y_labels)

        if render:
            grid_group.render()

        return grid_group


TRIG_CONFIG = CartesianGridConfig(
    step_x = np.pi/4,
    step_y = 1,
    show_numbers = True,
    x_label_format=pi_format,
    x_label_offset=(0, -30)
)
