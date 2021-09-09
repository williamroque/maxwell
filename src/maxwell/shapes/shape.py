import numpy as np

from maxwell.core.scene import Scene
from maxwell.core.frame import Frame

from maxwell.core.util import await_click

import datetime


class Shape():
    def move_to_point(self, point, n=None, fps=100, f=None, shapes=None, duration=.2, initial_clear=False):
        if shapes is None:
            shapes = []

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

        if n is None:
            n = int(duration * fps)

        if f is None:
            f = (np.sin, 0, np.pi)

        X = np.linspace(f[1], f[2], n)
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

