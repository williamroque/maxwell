"A cartesian coordinate system."

from dataclasses import dataclass
from copy import deepcopy

from typing import Callable

import numpy as np

from maxwell.core.coordinates.system import System
from maxwell.core.group import Group
from maxwell.core.util import pi_format, fraction_format
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.shape import ShapeConfig
from maxwell.shapes.latex import Latex, LatexConfig


@dataclass
class CartesianGridConfig:
    step_x: float = 1
    step_y: float = 1
    show_numbers: bool = True
    x_label_config: LatexConfig = LatexConfig(color='#555', font_size=9)
    y_label_config: LatexConfig = LatexConfig(color='#555', font_size=9, align='right')
    x_label_format: Callable = None
    y_label_format: Callable = None
    x_label_offset: tuple = (0, -20)
    y_label_offset: tuple = (-15, 15)


def default_formatter(x):
    if np.isclose(x, int(x)):
        return str(int(x))
    return '{:.2f}'.format(x)


class CartesianSystem(System):
    "The cartesian coordinate system"

    def scale_to_fit(self, curve, margin):
        "Scale the coordinate system to fit a curve + margin."

        quadrant_size = self.client.get_shape() / 2 - margin
        max_point = np.amax(np.abs(curve), axis=0)

        self.scale = quadrant_size / max_point


    def normalize(self, obj):
        if obj == []:
            return np.array(obj)

        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)

            points = obj * self.scale * np.array([1, -1]) + self.origin
            return points
        elif isinstance(obj, (int, float)):
            return obj * self.scale.sum()/2

        raise TypeError(f'Argument should be ndarray, list, tuple, or scalar. Type used: {type(obj)}.')


    def from_normalized(self, obj):
        if obj == []:
            return np.array(obj)

        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)

            points = (obj - self.origin) / (self.scale * np.array([1, -1]))
            return points
        elif isinstance(obj, (int, float)):
            return obj / (self.scale.sum()/2)

        raise TypeError(f'Argument should be ndarray, list, tuple, or scalar. Type used: {type(points)}.')


    def get_edges(self, edges):
        edges = edges.split()

        width, height = self.client.get_shape()
        left, top = self.from_normalized((0, 0))
        right, bottom = self.from_normalized((width, height))

        edge_key = {
            'left': left,
            'top': top,
            'right': right,
            'bottom': bottom
        }

        edges = [edge_key[edge] for edge in edges if edge in edge_key]

        if len(edges) > 1:
            return edges
        return edges[0]


    def plot(self, func, start=None, end=None, color=None, width=None, point_num=400, clip_factor=np.inf, endpoint=3, shade=None, render=True, invert=False, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        if invert:
            if start is None:
                start = self.get_edges('bottom')

            if end is None:
                end = self.get_edges('top')
        else:
            if start is None:
                start = self.get_edges('left')

            if end is None:
                end = self.get_edges('right')

        if isinstance(func, (float, int)):
            constant = func
            func = lambda x: constant

        if shape_config is None:
            shape_config = ShapeConfig()

        if curve_config is None:
            curve_config = deepcopy(Curve.DEFAULT_CURVE_CONFIG)

            if color is not None:
                curve_config.color = color

            if width is not None:
                curve_config.width = width

        shape_config.system = self

        x_values = np.linspace(start, end, point_num, endpoint=bool(endpoint & 2))[int(not endpoint & 1):]
        y_values = np.vectorize(func)(x_values).astype(float)

        if invert:
            x_values, y_values = y_values, x_values

        frame_height = abs(self.from_normalized(self.client.get_shape())[1])

        y_values[np.isnan(y_values)] = np.inf
        y_values[np.abs(y_values) > frame_height * clip_factor] = np.inf

        curve = Curve(zip(x_values, y_values), curve_config, shape_config)

        if render:
            curve.render()

        if shade is not None:
            point_num = int((shade[1] - shade[0]) / (end - start) * point_num)
            x_values = np.linspace(shade[0], shade[1], point_num, endpoint=bool(endpoint & 2))[int(not endpoint & 1):]
            y_values = np.vectorize(func)(x_values)

            if invert:
                x_values, y_values = y_values, x_values

                shade_points = list(zip(x_values, y_values))

                if len(shade) < 3:
                    shade_points.append((0, shade[1]))
                    shade_points.append((0, shade[0]))
                else:
                    shade_points += list(zip(
                        np.vectorize(shade[2])(y_values),
                        y_values
                    ))[::-1]
            else:
                shade_points = list(zip(x_values, y_values))

                if len(shade) < 3:
                    shade_points.append((shade[1], 0))
                    shade_points.append((shade[0], 0))
                else:
                    shade_points += list(zip(
                        x_values,
                        np.vectorize(shade[2])(x_values)
                    ))[::-1]

            shade_points.append((x_values[0], y_values[0]))

            color = curve_config.color
            if len(color) < 7:
                color = ''.join(sum(zip(color, color), ()))

            color = color.ljust(9, '1')

            shade_config = CurveConfig(
                color='transparent',
                fill_color=color
            )

            shade_curve = Curve(shade_points, shade_config, shape_config)

            if render:
                shade_curve.render()

            return curve, shade_curve

        return curve


    def parametric(self, x, y, start, end, color=None, point_num=400, endpoint=3, render=True, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        if isinstance(x, (float, int)):
            constant = x
            x = lambda _: constant

        if isinstance(y, (float, int)):
            constant = y
            y = lambda _: constant

        if shape_config is None:
            shape_config = ShapeConfig()

        if curve_config is None:
            curve_config = deepcopy(Curve.DEFAULT_CURVE_CONFIG)

            if color is not None:
                curve_config.color = color

        shape_config.system = self

        t_values = np.linspace(start, end, point_num, endpoint=bool(endpoint & 2))[int(not endpoint & 1):]
        x_values = np.vectorize(x)(t_values).astype(float)
        y_values = np.vectorize(y)(t_values).astype(float)

        x_values[np.isnan(x_values)] = np.inf
        y_values[np.isnan(y_values)] = np.inf

        curve = Curve(zip(x_values, y_values), curve_config, shape_config)

        if render:
            curve.render()

        return curve


    def get_grid(self, zoom_factor=None, translation=None, grid_config: CartesianGridConfig = None, render=True):
        if grid_config is None:
            grid_config = CartesianGridConfig()

        if zoom_factor is not None:
            self.zoom(zoom_factor)

            if isinstance(zoom_factor, (tuple, list, np.ndarray)):
                grid_config.step_x = 1/zoom_factor[0]
                grid_config.step_y = 1/zoom_factor[1]
            else:
                grid_config.step_x = 1/zoom_factor
                grid_config.step_y = 1/zoom_factor

        shape_config = ShapeConfig(client=self.client, system=self)
        axis_config = CurveConfig(width=2, color='#474747')

        width, height = self.client.get_shape()
        left, top = self.from_normalized((0, 0))
        right, bottom = self.from_normalized((width, height))

        x_count = int(np.ceil((abs(top) + abs(bottom)) / grid_config.step_y))
        y_count = int(np.ceil((abs(left) + abs(right)) / grid_config.step_x))

        if translation is None:
            translation = (0, 0)

        self.translate(translation)

        left, top = self.from_normalized((0, 0))
        right, bottom = self.from_normalized((width, height))

        x_label_offset = np.array(grid_config.x_label_offset)/self.scale
        y_label_offset = np.array(grid_config.y_label_offset)/self.scale

        grid_group = Group(background=True)

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

        offset_x = int(translation[0]/grid_config.step_x)
        offset_y = int(translation[1]/grid_config.step_y)

        for i in range(-x_count + offset_y, x_count + offset_y + 1):
            y = i * grid_config.step_y

            x_secondary = Curve(
                [
                    (left, y - grid_config.step_y/2),
                    (right, y - grid_config.step_y/2)
                ],
                curve_config=secondary_config,
                shape_config=shape_config
            )
            secondary_grid.add_shape(x_secondary, f'x-secondary-({i})')

            if i == 0:
                continue

            x_primary = Curve(
                [(left, y), (right, y)],
                curve_config=primary_config,
                shape_config=shape_config
            )
            primary_grid.add_shape(x_primary, f'x-primary-({i})')

            if grid_config.show_numbers:
                y = i * grid_config.step_y

                if grid_config.y_label_format is None:
                    label = default_formatter(y)
                else:
                    label = grid_config.y_label_format(y)

                label_shape = Latex(
                    label,
                    np.array((0, i * grid_config.step_y)) + y_label_offset,
                    latex_config=grid_config.y_label_config,
                    shape_config=shape_config
                )

                y_labels.add_shape(label_shape, f'y-label-{i}')

        for i in range(-y_count + offset_x, y_count + offset_x + 1):
            x = i * grid_config.step_x

            y_secondary = Curve(
                [
                    (x - grid_config.step_x/2, top),
                    (x - grid_config.step_x/2, bottom)
                ],
                curve_config=secondary_config,
                shape_config=shape_config
            )
            secondary_grid.add_shape(y_secondary, f'y-secondary-({i})')

            if i == 0:
                continue

            y_primary = Curve(
                [(x, top), (x, bottom)],
                curve_config=primary_config,
                shape_config=shape_config
            )
            primary_grid.add_shape(y_primary, f'y-primary-({i})')

            if grid_config.show_numbers:
                x = i * grid_config.step_x

                if grid_config.x_label_format is None:
                    label = default_formatter(x)
                else:
                    label = grid_config.x_label_format(x)

                label_shape = Latex(
                    label,
                    np.array((i * grid_config.step_x, 0)) + x_label_offset,
                    latex_config=grid_config.x_label_config,
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


TRIG = CartesianGridConfig(
    step_x = np.pi/4,
    step_y = 1,
    show_numbers = True,
    x_label_format=pi_format,
    x_label_offset=(0, -30)
)


FRACTION = CartesianGridConfig(
    show_numbers = True,
    x_label_format=fraction_format,
    x_label_offset=(0, -30),
    y_label_format=fraction_format
)
