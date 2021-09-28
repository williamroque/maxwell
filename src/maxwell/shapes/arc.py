from dataclasses import dataclass

import numpy as np

from maxwell.shapes.shape import Shape, ShapeConfig

from maxwell.core.animation import AnimationConfig
from maxwell.core.properties import Properties
from maxwell.core.scene import Scene
from maxwell.core.frame import Frame


@dataclass
class ArcConfig:
    radius: int = 7
    theta_1: float = 0
    theta_2: float = 2*np.pi
    color: str = '#fff'
    border_color: str = 'transparent'
    border_width: int = 1


class Arc(Shape):
    DEFAULT_ARC_CONFIG = None

    def __init__(self, point=None, arc_config: ArcConfig = None, shape_config: ShapeConfig = None):

        if point is None:
            point = np.array((0, 0))

        super().__init__(shape_config)

        if arc_config is None:
            arc_config = self.default_config('arc_config', ArcConfig)

        self.properties = Properties(
            type = 'arc',
            point = point,
            radius = arc_config.radius,
            theta_1 = -arc_config.theta_1,
            theta_2 = -arc_config.theta_2,
            fillColor = arc_config.color,
            borderColor = arc_config.border_color,
            borderWidth = arc_config.border_width
        )
        self.properties.set_normalized('point')


    @staticmethod
    def follow_path_apply(frame, props):
        "Callback for follow_path frames."

        point = props.path(
            props.i * 1/props.fps,
            props.i,
            frame.props(props.shape_name).point,
        )

        frame.props(props.shape_name).point = point

        props.i += 1


    def follow_path(self, path_function, animation_config: AnimationConfig = None):
        if animation_config is None:
            animation_config = AnimationConfig()

        scene_properties = {
            'fps': animation_config.fps,
            'path': path_function,
            'shape_name': self.shape_name
        }

        scene, frame_num = self.create_scene(scene_properties, animation_config)

        scene.repeat_frame(frame_num, Arc.follow_path_apply)

        return scene
