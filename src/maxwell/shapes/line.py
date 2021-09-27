"System for curves and all manner of line-based shapes."

from dataclasses import dataclass

import numpy as np

from maxwell.shapes.shape import Shape, ShapeConfig

from maxwell.core.animation import AnimationConfig
from maxwell.core.properties import Properties
from maxwell.core.scene import Scene
from maxwell.core.frame import Frame
from maxwell.core.util import rotate
from maxwell.core.group import Group


@dataclass
class CurveConfig:
    color: str = '#fff'
    width: int = 3
    arrows: int = 0
    arrow_size: float = 6


class Curve(Shape):
    "A class for lines and a superclass for line-based shapes."

    def __init__(self, points, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        "A class for lines and a superclass for line-based shapes."

        super().__init__(shape_config)

        if curve_config is None:
            curve_config = CurveConfig()

        if isinstance(points, Group):
            point_list = []

            for shape in points.shapes.values():
                point_list.append([shape.properties.x, shape.properties.y])

            points = point_list

        self.properties = Properties(
            type = 'lineset',
            points = list(map(list, list(points))),
            color = curve_config.color,
            width = curve_config.width,
            arrows = curve_config.arrows,
            arrowSize = curve_config.arrow_size
        )
        self.properties.set_normalized('points')


    @classmethod
    def from_function(cls, func, start, end, point_num, **kwargs):
        "Create a `Curve` instance from a mathematical function."

        x_values = np.linspace(start, end, point_num)
        y_values = func(x_values)

        return cls(zip(x_values, y_values), **kwargs)


    @staticmethod
    def from_functions(funcs, *args, **kwargs):
        "Create several `Curve` instances from mathematical functions."

        return [Curve.from_function(func, *args, **kwargs) for func in funcs]


    def set_points(self, points):
        "Change the curve's points."

        self.properties.points = list(map(list, list(points)))


    @staticmethod
    def move_point_setup(frame, props):
        "Frame setup for `move_point`."

        props.cx = props.ending_point[0] - props.point[0]
        props.cy = props.ending_point[1] - props.point[1]


    @staticmethod
    def move_point_apply(frame, props):
        "Frame callback for `move_point`."

        x_change = props.cx * props.easing_ratio
        y_change = props.cy * props.easing_ratio

        props.point[0] += x_change
        props.point[1] += y_change


    def move_point(self, point_i, ending_point, animation_config: AnimationConfig = None):
        "Create a scene moving a specific point."

        scene_properties = {
            'cx': None,
            'cy': None,
            'point': self.properties.points[point_i],
            'ending_point': ending_point
        }

        scene, frame_num = self.create_scene(scene_properties, animation_config)

        scene.repeat_frame(
            frame_num,
            Curve.move_point_apply,
            Curve.move_point_setup
        )

        return scene

    def move_end(self, point, *args, **kwargs):
        "Create a scene moving the last point."

        return self.move_point(len(self.properties.points) - 1, point, *args, **kwargs)


    def rotate_about(self, origin, theta, n=None, n_scale=1, f=None, animate=True, shapes=[]):
        "Create a scene moving the curve about a specific point."

        if not animate:
            self.properties.points = rotate(self.properties.points, origin, theta)

            return self

        scene = Scene(self.client, { 'i': 0, 'shape_name': self.shape_name })

        scene.add_shape(self)

        scene.add_background(shapes)

        if n is None:
            n = int(abs(theta) * 100 * n_scale)

        if f is None:
            f = (np.sin, 0, np.pi)

        X = np.linspace(f[1], f[2], n)
        Y = np.abs(f[0](X))
        C = Y / Y.sum()

        class MotionFrame(Frame):
            def apply_frame(self, props):
                d_theta = C[props.i] * theta

                shape_name = props.shape_name

                self.props(shape_name).properties.points = rotate(
                    self.props(shape_name).points,
                    origin,
                    d_theta
                )

                props.i += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return scene


    @staticmethod
    def transform_setup(frame, props):
        "Callback for transformation frames setup."

        for j, point in enumerate(props.points):
            target_x, target_y = props.target_curve[j]

            props.cx.append(target_x - point[0])
            props.cy.append(target_y - point[1])


    @staticmethod
    def transform_apply(frame, props):
        "Callback for transformation frames."

        for j, point in enumerate(props.points):
            ratio = props.easing_ratio

            x_change = props.cx[j] * ratio
            y_change = props.cy[j] * ratio

            props.points[j][0] += x_change
            props.points[j][1] += y_change


    def transform(self, target_curve, animation_config: AnimationConfig = None):
        "Create a scene transforming the curve into another one."

        if isinstance(target_curve, Curve):
            target_curve = target_curve.properties.points

        target_curve = list(target_curve)

        scene_properties = {
            'cx': [],
            'cy': [],
            'points': self.properties.points,
            'target_curve': target_curve,
        }

        scene, frame_num = self.create_scene(
            scene_properties,
            animation_config
        )

        scene.repeat_frame(
            frame_num,
            Curve.transform_apply,
            Curve.transform_setup
        )

        return scene
