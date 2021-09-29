"A cartesian coordinate system."

from dataclasses import dataclass

import numpy as np

from maxwell.core.coordinates.system import System
from maxwell.core.group import Group
from maxwell.core.util import pi_format
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.shape import ShapeConfig
from maxwell.shapes.latex import Latex


@dataclass
class PolarGridConfig:
    step_r: float = 1
    step_theta: float = np.pi/6
    theta_offset: float = np.pi/4 - np.pi/6
    show_radii: bool = True
    show_angles: bool = False
    ring_label_offset: tuple = (0, 17)
    line_label_offset: tuple = (0, 0)


class PolarSystem(System):
    "The polar coordinate system"

    @staticmethod
    def to_cartesian(point):
        r, theta = point
        x = r*np.cos(theta)
        y = r*np.sin(theta)
        return x, y


    @staticmethod
    def to_polar(point):
        x, y = point
        r = np.hypot(x, y)
        theta = np.arctan2(y, x)
        return r, theta


    def plot(self, func, start, end, point_num=400, render=True, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        if shape_config is None:
            shape_config = ShapeConfig()

        shape_config.system = self

        theta = np.linspace(start, end, point_num)
        r = func(theta)

        curve = Curve(zip(r, theta), curve_config, shape_config)

        if render:
            curve.render()

        return curve


    def normalize(self, obj):
        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)
            obj = np.apply_along_axis(PolarSystem.to_cartesian, -1, obj)

            points = obj * self.scale * np.array([1, -1]) + self.origin
            return points

        raise TypeError(f'Argument should be ndarray, list, or tuple. Type used: {type(obj)}.')


    def from_normalized(self, obj):
        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)

            points = (obj - self.origin) / (self.scale * np.array([1, -1]))
            points = np.apply_along_axis(PolarSystem.to_polar, -1, points)

            return points

        raise TypeError(f'Argument should be ndarray, list, or tuple. Type used: {type(points)}.')


    def theta_label(self, point, offset):
        shape_config = ShapeConfig(client=self.client, system=self)

        label_shape = Latex(
            pi_format(point[1]),
            self.apply_offset(point, offset),
            shape_config=shape_config
        )
        return label_shape


    def get_grid(self, grid_config: PolarGridConfig = None):
        if grid_config is None:
            grid_config = PolarGridConfig()

        shape_config = ShapeConfig(client=self.client, system=self)
        axis_config = CurveConfig(width=2, color='#474747')

        client_shape = self.client.get_shape()
        left, top = self.origin / self.scale[1]
        right, bottom = (client_shape - self.origin) / self.scale[1]

        grid_group = Group()

        x_axis = Curve(
            [(left, np.pi), (right, 0)],
            curve_config=axis_config,
            shape_config=shape_config
        )
        grid_group.add_shape(x_axis, 'x-axis')

        y_axis = Curve(
            [(top, np.pi/2), (bottom, 3*np.pi/2)],
            curve_config=axis_config,
            shape_config=shape_config
        )
        grid_group.add_shape(y_axis, 'y-axis')

        max_length = max(left, right, top, bottom)
        ring_count = int(max_length / grid_config.step_r + 2)

        primary_rings = Group()
        secondary_rings = Group()

        ring_labels = Group()

        primary_config = CurveConfig(width=2, color='#4447')
        secondary_config = CurveConfig(width=1, color='#6664')

        for i in range(ring_count):
            primary_radius = (i + 1) * grid_config.step_r
            secondary_radius = (i + 1/2) * grid_config.step_r

            primary_ring = self.plot(
                lambda theta: np.full_like(theta, primary_radius),
                0, 2*np.pi, render=False, curve_config = primary_config
            )
            primary_rings.add_shape(primary_ring, f'primary-ring-{i}')

            secondary_ring = self.plot(
                lambda theta: np.full_like(theta, secondary_radius),
                0, 2*np.pi, render=False, curve_config = secondary_config
            )
            secondary_rings.add_shape(secondary_ring, f'secondary-ring-{i}')

            if grid_config.show_radii:
                label_shape = Latex(
                    str(primary_radius),
                    self.apply_offset((primary_radius, 0), grid_config.ring_label_offset),
                    shape_config=shape_config
                )

                ring_labels.add_shape(label_shape, f'ring-label-{i}')

        grid_group.merge_with(primary_rings)
        grid_group.merge_with(secondary_rings)
        grid_group.merge_with(ring_labels)

        line_count = int(np.pi / grid_config.step_theta)

        primary_lines = Group()
        secondary_lines = Group()
        line_labels = Group()

        for i in range(line_count):
            theta = i * grid_config.step_theta
            minor_theta = theta - grid_config.theta_offset
            major_theta = theta + grid_config.theta_offset

            if np.isclose(theta % (np.pi/2), 0):
                continue

            primary_line = Curve(
                [
                    (-np.hypot(left, bottom), theta),
                    (np.hypot(right, top), theta)
                ],
                curve_config = primary_config
            )
            primary_lines.add_shape(primary_line, f'primary-line-{i}')

            minor_secondary_line = Curve(
                [
                    (-np.hypot(left, bottom), minor_theta),
                    (np.hypot(right, top), minor_theta)
                ],
                curve_config = secondary_config
            )
            secondary_lines.add_shape(minor_secondary_line, f'minor-secondary-line-{i}')

            major_secondary_line = Curve(
                [
                    (-np.hypot(left, bottom), major_theta),
                    (np.hypot(right, top), major_theta)
                ],
                curve_config = secondary_config
            )
            secondary_lines.add_shape(major_secondary_line, f'major-secondary-line-{i}')

            line_label_radius = max_length / 2

            if grid_config.show_angles:
                line_labels.add_shape(
                    self.theta_label((line_label_radius, theta), grid_config.line_label_offset),
                    f'line-label-{i}'
                )
                line_labels.add_shape(
                    self.theta_label((line_label_radius, theta + np.pi), grid_config.line_label_offset),
                    f'line-opposite-label-{i}'
                )

                line_labels.add_shape(
                    self.theta_label((line_label_radius, minor_theta), grid_config.line_label_offset),
                    f'minor-line-label-{i}'
                )
                line_labels.add_shape(
                    self.theta_label((line_label_radius, minor_theta + np.pi), grid_config.line_label_offset),
                    f'minor-line-opposite-label-{i}'
                )

                line_labels.add_shape(
                    self.theta_label((line_label_radius, major_theta), grid_config.line_label_offset),
                    f'major-line-label-{i}'
                )
                line_labels.add_shape(
                    self.theta_label((line_label_radius, major_theta + np.pi), grid_config.line_label_offset),
                    f'major-line-opposite-label-{i}'
                )

        grid_group.merge_with(primary_lines)
        grid_group.merge_with(secondary_lines)
        grid_group.merge_with(line_labels)

        return grid_group
