import numpy as np

from maxwell.core.scene import Scene
from maxwell.core.frame import Frame

from maxwell.core.util import await_click, create_easing_function, rgb_to_hex, hex_to_rgb

import datetime


class Shape():
    def create_scene(self, properties, duration=2, fps=100, easing_function=None, shapes=None):
        frame_num = int(duration * fps)

        if easing_function is None:
            easing_function = create_easing_function(frame_num)

        properties['easing_function'] = easing_function

        scene = Scene(self.client, properties)

        scene.add_shape(self)

        if shapes is not None:
            scene.add_background(shapes)

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


    def change_color(self, target_color, rgb=False, **kwargs):
        "Transition from current color to target color."

        if not rgb:
            target_color = hex_to_rgb(target_color)

        scene_properties = {
            'shape_name': self.shape_name,
            'target_color': target_color
        }

        scene, frame_num = self.create_scene(scene_properties, **kwargs)

        scene.repeat_frame(frame_num, Shape.change_color_apply, Shape.change_color_setup)

        return scene


    def set_opacity(self, opacity):
        "Set opacity without animating."

        color = hex_to_rgb(self.properties.color)
        color[3] = opacity * 255

        self.properties.color = rgb_to_hex(color)


    def show(self, **kwargs):
        "Animate showing shape (opacity-wise)."

        color = hex_to_rgb(self.properties.color)
        color[3] = 255

        return self.change_color(color, rgb=True, **kwargs)


    def hide(self, **kwargs):
        "Animate hiding shape (opacity-wise)."

        color = hex_to_rgb(self.properties.color)
        color[3] = 0

        return self.change_color(color, rgb=True, **kwargs)


    def move_to_point(self, point, fps=100, f=None, shapes=None, duration=.2, initial_clear=False):
        if shapes is None:
            shapes = []

        frame_num = int(duration * fps)

        starting_point = [
            self.properties.x,
            self.properties.y
        ]

        scene = Scene(self.client, {
            'i': 0,
            'cx': None,
            'cy': None,
            'final_x': point[0],
            'final_y': point[1],
            'shape_name': self.shape_name
        })

        scene.add_shape(self)

        scene.add_background(shapes, self)

        if f is None:
            f = (np.sin, 0, np.pi)

        X = np.linspace(f[1], f[2], frame_num)
        Y = np.abs(f[0](X))
        C = Y / Y.sum()

        class MotionFrame(Frame):
            def apply_frame(self, props):
                shape_name = props.shape_name

                if props.i == 0:
                    props.cx = props.final_x - self.props(shape_name).x
                    props.cy = props.final_y - self.props(shape_name).y

                self.props(shape_name).x += props.cx * C[props.i]
                self.props(shape_name).y += props.cy * C[props.i]

                props.i += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return scene


    def move_to(self, other_shape, n=None, dt=.01, f=None, shapes=[]):
        ending_point = [
            other_shape.properties.x,
            other_shape.properties.y
        ]

        return self.move_to_point(ending_point, n, dt, f, shapes + [other_shape])


    def follow(self, animate=True, shapes=[]):
        point = [None, None]

        while not (props := await_click(self.client, 'altKey'))[2]:
            point = props[:2]

            if hasattr(self, 'system') and self.system is not None:
                point = self.system.from_normalized(point)

            if animate:
                scene = self.move_to_point(point, dt=.005, f=(np.sin, 0, np.pi), shapes=shapes, initial_clear=bool(shapes))
            else:
                scene = self.move_to_point(point, n = 1, shapes=shapes)

            if shapes:
                shapes = []

            scene.play()

        return point

