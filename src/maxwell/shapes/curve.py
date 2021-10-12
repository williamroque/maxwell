"System for curves and all manner of line-based shapes."

from dataclasses import dataclass

import numpy as np

from maxwell.shapes.shape import Shape, ShapeConfig

from maxwell.core.animation import AnimationConfig
from maxwell.core.properties import Properties
from maxwell.core.util import rotate
from maxwell.core.group import Group


@dataclass
class CurveConfig:
    color: str = '#fdf4c1'
    width: int = 3
    arrow: bool = False
    arrow_size: float = .07
    clip: np.typing.ArrayLike = (-1, -1)
    fill_color: str = 'transparent'


class Curve(Shape):
    "A class for lines and a superclass for line-based shapes."

    DEFAULT_CURVE_CONFIG = CurveConfig()

    def __init__(self, points, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        "A class for lines and a superclass for line-based shapes."

        super().__init__(shape_config)

        if curve_config is None:
            curve_config = self.get_default('curve_config')

        if isinstance(points, Group):
            point_list = []

            for shape in points.shapes.values():
                point_list.append([shape.properties.x, shape.properties.y])

            points = point_list

        self.arrow = curve_config.arrow
        self.arrow_size = curve_config.arrow_size

        if curve_config.arrow:
            arrow_head = self.compute_arrow_head(points[-2], points[-1])
        else:
            arrow_head = []

        self.properties = Properties(
            type = 'curve',
            points = list(map(list, list(points))),
            color = curve_config.color,
            width = curve_config.width,
            arrowHead = arrow_head,
            clip = curve_config.clip,
            fillColor = curve_config.fill_color
        )
        self.properties.set_normalized('points', 'arrowHead', 'clip')

        if self.auto_render:
            self.render()


    def compute_arrow_head(self, penultimate, ultimate):
        penultimate = np.array(penultimate)
        ultimate = np.array(ultimate)

        alpha = 2*np.pi/3
        difference = ultimate - penultimate
        r = np.linalg.norm(difference)
        x, y = difference
        theta = np.arctan2(y, x)

        points = []

        for i in range(3):
            point = np.array([
                np.cos(theta + i*alpha) - np.cos(theta),
                np.sin(theta + i*alpha) - np.sin(theta)
            ])

            points.append((self.arrow_size*point + ultimate).tolist())

        return points


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

        shape = frame.scene.shapes[props.shape_name]

        if shape.arrow:
            frame.props(props.shape_name).arrowHead = shape.compute_arrow_head(
                shape.properties.points[-2],
                shape.properties.points[-1]
            )


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


    @staticmethod
    def rotate_about_apply(frame, props):
        "Frame callback for rotate_about."

        shape_name = props.shape_name

        frame.props(shape_name).points = rotate(
            frame.props(shape_name).points,
            props.origin,
            props.angle * props.easing_ratio
        )


    def rotate_about(self, origin, theta, animate=False, animation_config: AnimationConfig = None):
        "Create a scene moving the curve about a specific point."

        if not animate:
            self.properties.points = rotate(self.properties.points, origin, theta)

            return self

        scene_properties = {
            'origin': origin,
            'angle': theta
        }

        scene, frame_num = self.create_scene(scene_properties, animation_config)

        scene.repeat_frame(
            frame_num,
            Curve.rotate_about_apply
        )

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

        shape = frame.scene.shapes[props.shape_name]

        if shape.arrow:
            frame.props(props.shape_name).arrowHead = shape.compute_arrow_head(
                props.points[-2],
                props.points[-1]
            )


    def transform(self, target_curve, animation_config: AnimationConfig = None):
        "Create a scene transforming the curve into another one."

        color_scene = None

        if isinstance(target_curve, Curve):
            color_scene = self.change_color(
                target_curve.properties.color,
                animation_config = animation_config
            )
            target_curve = target_curve.properties.points

        target_curve = list(target_curve)

        scene_properties = {
            'cx': [],
            'cy': [],
            'points': self.properties.points,
            'target_curve': target_curve,
            'shape_name': self.shape_name
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

        if color_scene is not None:
            scene.link_scene(color_scene)

        return scene
