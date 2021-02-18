import numpy as np

from maxwell.core.scene import Scene, TransformationScene
from maxwell.core.frame import Frame

from maxwell.core.util import await_click

import datetime


class Shape():
    def move_to_point(self, point, n=None, dt=.01, f=None, shapes=[], duration=.2):
        scene = Scene(self.client, { 'i': 0 })

        shape_name = f'{datetime.datetime.now()}-shape'
        scene.add_shape(self, shape_name)

        for i, shape in enumerate(shapes):
            scene.add_shape(shape, f'{datetime.datetime.now()}-{i}-shape', True)

        starting_point = [
            self.properties.x,
            self.properties.y
        ]

        cx = point[0] - starting_point[0]
        cy = point[1] - starting_point[1]
        r = np.hypot(cx, cy)

        if n is None:
            n = int(duration / dt)

        if f is None:
            f = (lambda x: 0 * x + 1 / n, 0, 1)

        X = np.linspace(f[1], f[2], n)
        Y = np.abs(f[0](X))
        C = Y / Y.sum()

        class MotionFrame(Frame):
            def apply_frame(self, props):
                dx = cx * C[props.i]
                dy = cy * C[props.i]

                self.scene.shapes[shape_name].properties.x += dx
                self.scene.shapes[shape_name].properties.y += dy

                props.i += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return TransformationScene(scene, dt)

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
                scene = self.move_to_point(point, dt=.005, f=(lambda x: np.sin(x), 0, np.pi), shapes=shapes)
            else:
                scene = self.move_to_point(point, n = 1, shapes=shapes)

            if shapes:
                shapes = []

            scene.play()

        return point

