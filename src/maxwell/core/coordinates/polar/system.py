"A cartesian coordinate system."

from dataclasses import dataclass
from copy import deepcopy

import numpy as np

from maxwell.core.coordinates.system import System
from maxwell.core.group import Group
from maxwell.core.util import pi_format, is_light_mode
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.shape import ShapeConfig
from maxwell.shapes.latex import Latex, LatexConfig


@dataclass
class PolarGridConfig:
    step_r: float = 1
    primary_sections: int = 2
    secondary_sections: int = 3
    show_axis: bool = True
    show_radii: bool = True
    show_primary_angles: bool = True
    show_secondary_angles: bool = False
    ring_label_offset: tuple = (10, 17)
    line_label_offset: tuple = (0, 0)
    ring_label_config: LatexConfig = LatexConfig(color='#444', font_size=8)
    primary_label_config: LatexConfig = LatexConfig(color='#444', font_size=11)
    secondary_label_config: LatexConfig = LatexConfig(color='#555', font_size=8)


def near_multiple(a, b):
    div = a / b

    return np.isclose(div - round(div), 0)


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


    def plot(self, func, start, end, color=None, point_num=400, render=True, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        if shape_config is None:
            shape_config = ShapeConfig()


        if curve_config is None:
            curve_config = deepcopy(Curve.DEFAULT_CURVE_CONFIG)
            
            if color is None:
                if is_light_mode(self.client):
                    curve_config.color = '#121112'
            else:
                curve_config.color = color

        shape_config.system = self

        theta = np.linspace(start, end, point_num)
        r = np.vectorize(func)(theta)

        curve = Curve(zip(r, theta), curve_config, shape_config)

        if render:
            curve.render()

        return curve


    def normalize(self, obj):
        if obj == []:
            return np.array(obj)

        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)
            obj = np.apply_along_axis(PolarSystem.to_cartesian, -1, obj)

            points = obj * self.scale * np.array([1, -1]) + self.origin
            return points

        raise TypeError(f'Argument should be ndarray, list, or tuple. Type used: {type(obj)}.')


    def from_normalized(self, obj):
        if obj == []:
            return np.array(obj)

        if isinstance(obj, (np.ndarray, list, tuple)):
            obj = np.array(obj)

            points = (obj - self.origin) / (self.scale * np.array([1, -1]))
            points = np.apply_along_axis(PolarSystem.to_polar, -1, points)

            return points

        raise TypeError(f'Argument should be ndarray, list, or tuple. Type used: {type(points)}.')


    def get_rings(self, max_radius, grid_config: PolarGridConfig, shape_config: ShapeConfig):
        ring_count = int(max_radius / grid_config.step_r + 1)

        ring_group = Group()

        primary_config = CurveConfig(width=2, color='#4447')
        secondary_config = CurveConfig(width=1, color='#6664')

        primary_rings = Group()
        secondary_rings = Group()

        ring_labels = Group()

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
                    latex_config=grid_config.ring_label_config,
                    shape_config=shape_config
                )

                ring_labels.add_shape(label_shape, f'ring-label-{i}')

        ring_group.merge_with(primary_rings)
        ring_group.merge_with(secondary_rings)
        ring_group.merge_with(ring_labels)

        return ring_group


    def get_radial_lines(self, max_length, max_radius, grid_config: PolarGridConfig, shape_config: ShapeConfig):
        primary_config = CurveConfig(width=2, color='#4447')
        secondary_config = CurveConfig(width=1, color='#6664')

        lines_group = Group()

        primary_lines = Group()
        secondary_lines = Group()
        line_labels = Group()

        def create_section(theta, config, group, label_config, show_label):
            line = Curve(
                [
                    (0, 0),
                    (max_radius, theta)
                ],
                curve_config = config,
                shape_config = shape_config
            )
            group.add_shape(line)

            if show_label:
                label_shape = Latex(
                    pi_format(theta),
                    self.apply_offset((max_length / 2, theta), grid_config.line_label_offset),
                    latex_config = label_config,
                    shape_config = shape_config
                )
                group.add_shape(label_shape)

        for quadrant in range(4):
            quadrant_theta = quadrant * np.pi/2
            quadrant_size = np.pi/2
            primary_section_size = quadrant_size / grid_config.primary_sections
            secondary_section_size = primary_section_size / grid_config.secondary_sections

            for primary_section in range(grid_config.primary_sections):
                primary_theta = quadrant_theta + primary_section*primary_section_size

                create_section(
                    primary_theta,
                    primary_config,
                    primary_lines,
                    grid_config.primary_label_config,
                    grid_config.show_primary_angles
                )

                for secondary_section in range(1, grid_config.secondary_sections):
                    secondary_theta = primary_theta + secondary_section*secondary_section_size

                    create_section(
                        secondary_theta,
                        secondary_config,
                        secondary_lines,
                        grid_config.secondary_label_config,
                        grid_config.show_secondary_angles
                    )

        lines_group.merge_with(primary_lines)
        lines_group.merge_with(secondary_lines)
        lines_group.merge_with(line_labels)

        return lines_group


    def get_grid(self, grid_config: PolarGridConfig = None, render=True):
        if grid_config is None:
            grid_config = PolarGridConfig()

        shape_config = ShapeConfig(client=self.client, system=self)

        client_shape = self.client.get_shape()
        left, top = self.origin / self.scale[1]
        right, bottom = (client_shape - self.origin) / self.scale[1]

        grid_group = Group()

        if grid_config.show_axis:
            axis_config = CurveConfig(width=2, color='#474747')

            polar_axis = Curve(
                [(0, 0), (right, 0)],
                curve_config=axis_config,
                shape_config=shape_config
            )
            grid_group.add_shape(polar_axis, 'polar-axis')

        max_length = max(left, right, top, bottom)
        max_radius = np.hypot(right, top)

        grid_group.merge_with(
            self.get_rings(max_radius, grid_config, shape_config)
        )

        grid_group.merge_with(
            self.get_radial_lines(max_length, max_radius, grid_config, shape_config)
        )

        if render:
            grid_group.render()

        return grid_group
