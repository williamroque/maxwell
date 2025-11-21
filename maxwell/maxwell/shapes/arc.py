from dataclasses import dataclass, replace

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
    color: str = '#fdf4c1'
    border_color: str = 'transparent'
    border_width: int = 1


class Arc(Shape):
    DEFAULT_ARC_CONFIG = ArcConfig()

    def __init__(self, point=None, color=None, arc_config: ArcConfig = None, shape_config: ShapeConfig = None):
        super().__init__(shape_config)

        if point is None:
            point = [0, 0]

        if arc_config is None:
            arc_config = self.get_default('arc_config')

        if color is not None:
            arc_config = replace(arc_config, color=color)

        self.properties = Properties(
            type = 'arc',
            point = list(point),
            radius = arc_config.radius,
            theta_1 = -arc_config.theta_1,
            theta_2 = -arc_config.theta_2,
            fillColor = arc_config.color,
            borderColor = arc_config.border_color,
            borderWidth = arc_config.border_width
        )
        self.properties.set_normalized('point')

        if self.auto_render:
            self.render()


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
