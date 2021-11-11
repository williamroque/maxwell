import datetime

from dataclasses import dataclass, replace

from maxwell.client.client import Client
from maxwell.client.message import Message

from maxwell.core.scene import Scene

from maxwell.core.util import await_click
from maxwell.core.animation import create_easing_function, AnimationConfig
from maxwell.core.util import rgb_to_hex, hex_to_rgb


@dataclass
class ShapeConfig:
    client: Client = None
    system: 'System' = None
    group: 'Group' = None
    shape_name: str = None
    render: bool = False
    canvas: str = 'default'


class Shape:
    "The shape superclass."

    DEFAULT_CLIENT = None
    DEFAULT_SYSTEM = None
    DEFAULT_SHAPE_CONFIG = ShapeConfig()
    DEFAULT_ANIMATION_CONFIG = AnimationConfig()

    def __init__(self, shape_config: ShapeConfig = None):
        "The shape superclass."

        if shape_config is None:
            shape_config = self.get_default('shape_config')

        self.client = shape_config.client
        if self.client is None:
            default_client = self.get_default('client')

            if default_client is None:
                raise ValueError("Client specification required. Consider setting DEFAULT_CLIENT.")

            self.client = default_client

        self.system = shape_config.system
        if self.system is None:
            self.system = self.get_default('system')

        self.group = shape_config.group

        self.shape_name = shape_config.shape_name
        if self.shape_name is None:
            self.shape_name = f'{datetime.datetime.now()}-shape'

        if self.group is not None:
            self.group.add_shape(self)

        self.auto_render = shape_config.render

        self.canvas = shape_config.canvas

        self.access_hooks = []


    def get_default(self, attribute):
        "Get class default using short form of attribute."

        expanded_attribute = 'DEFAULT_{}'.format(attribute.upper())

        return getattr(self.__class__, expanded_attribute)


    @classmethod
    def set_default(cls, attribute, value):
        "Set class default using short form of attribute."

        expanded_attribute = 'DEFAULT_{}'.format(attribute.upper())

        return setattr(cls, expanded_attribute, value)


    @classmethod
    def set_config(cls, config_id, **kwargs):
        "Convenient way to set default config."

        expanded_attribute = 'DEFAULT_{}'.format(config_id.upper())

        config = getattr(cls, expanded_attribute)
        setattr(cls, expanded_attribute, replace(config, **kwargs))


    @classmethod
    def auto(cls):
        "Toggle auto-render shape on init."

        default_config = cls.DEFAULT_SHAPE_CONFIG
        cls.DEFAULT_SHAPE_CONFIG = replace(default_config, render=(not default_config.render))


    def add_access_hook(self, callback, *args):
        self.access_hooks.append((callback, args))


    def get_props(self):
        "Extract shape rendering properties."

        for access_hook, args in self.access_hooks:
            access_hook(self, *args)

        return self.properties.get_normalized(self.system)


    def create_scene(self, properties, animation_config: AnimationConfig = None):
        if animation_config is None:
            animation_config = self.get_default('animation_config')

        frame_num = int(animation_config.duration * animation_config.fps)

        easing_function = create_easing_function(
            frame_num,
            *animation_config.easing_function
        )

        properties['easing_function'] = easing_function
        properties['shape_name'] = self.shape_name

        scene = Scene(self.client, properties)

        scene.add_shape(self)

        if animation_config.shapes is not None:
            scene.add_background(animation_config.shapes)

        return scene, frame_num


    @staticmethod
    def change_color_setup(frame, props):
        "Setup for change_color frames."

        original_color = frame.props(props.shape_name).color
        original_color = hex_to_rgb(original_color)

        props.shape_color = original_color
        props.total_change = props.target_color - props.shape_color


    @staticmethod
    def change_color_apply(frame, props):
        "Callback for change_color frames."

        shape = frame.props(props.shape_name)

        color_change = props.easing_ratio * props.total_change
        color = props.shape_color + color_change

        props.shape_color = color

        shape.color = rgb_to_hex(props.shape_color)


    def change_color(self, target_color, rgb=False, animation_config: AnimationConfig = None):
        "Transition from current color to target color."

        if not rgb:
            target_color = hex_to_rgb(target_color)

        scene_properties = {
            'target_color': target_color
        }

        scene, frame_num = self.create_scene(scene_properties, animation_config)

        scene.repeat_frame(frame_num, Shape.change_color_apply, Shape.change_color_setup)

        return scene


    def set_opacity(self, opacity):
        "Set opacity without animating."

        color = hex_to_rgb(self.properties.color)
        color[3] = opacity * 255

        self.properties.color = rgb_to_hex(color)


    def show(self, animation_config: AnimationConfig = None):
        "Animate showing shape (opacity-wise)."

        color = hex_to_rgb(self.properties.color)
        color[3] = 255

        return self.change_color(color, True, animation_config)


    def hide(self, animation_config: AnimationConfig = None):
        "Animate hiding shape (opacity-wise)."

        color = hex_to_rgb(self.properties.color)
        color[3] = 0

        return self.change_color(color, True, animation_config)


    @staticmethod
    def move_to_point_setup(frame, props):
        "Setup for move_to_point frames."

        props.cx = props.final_x - frame.props(props.shape_name).point[0]
        props.cy = props.final_y - frame.props(props.shape_name).point[1]


    @staticmethod
    def move_to_point_apply(frame, props):
        "Callback for move_to_point frames."

        frame.props(props.shape_name).point[0] += props.cx * props.easing_ratio
        frame.props(props.shape_name).point[1] += props.cy * props.easing_ratio


    def move_to_point(self, point, animation_config: AnimationConfig = None):
        scene_properties = {
            'cx': None,
            'cy': None,
            'final_x': point[0],
            'final_y': point[1]
        }

        scene, frame_num = self.create_scene(scene_properties,
                                             animation_config)

        scene.repeat_frame(frame_num, Shape.move_to_point_apply,
                           Shape.move_to_point_setup)

        return scene


    def move_to(self, other_shape, animation_config: AnimationConfig = None):
        return self.move_to_point(other_shape.properties.point, animation_config)


    def follow(self, animation_config: AnimationConfig = None):
        point = [None, None]

        while not (props := await_click(self.client, 'altKey'))[2]:
            point = props[:2]

            if self.system is not None:
                point = self.system.from_normalized(point)

            scene = self.move_to_point(point, animation_config)
            scene.play()

        return point


    def render(self, background=False):
        message = Message(
            self.client,
            'draw',
            args=self.get_props(),
            canvas='background' if background else self.canvas
        )
        message.send()

        return self
