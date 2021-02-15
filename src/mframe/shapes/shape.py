import numpy as np

from mframe.core.scene import Scene
from mframe.core.frame import Frame

import datetime


class Shape():
    def move_to_point(self, point, n=None, dt=.01, f=None, shapes=[]):
        scene = Scene(self.client, { 'i': 0 })

        shape_name = f'{datetime.datetime.now()}-shape'
        scene.add_shape(self, shape_name)

        for i, shape in enumerate(shapes):
            scene.add_shape(shape, f'{datetime.datetime.now()}-{i}-shape')

        starting_point = [
            self.properties['x'],
            self.properties['y']
        ]

        cx = point[0] - starting_point[0]
        cy = point[1] - starting_point[1]
        r = np.hypot(cx, cy)

        if n is None:
            n = int(r / 2)

        if f is None:
            f = (lambda x: 0 * x + 1 / n, 0, 1)

        X = np.linspace(f[1], f[2], n)
        Y = np.abs(f[0](X))
        C = Y / Y.sum()

        class MotionFrame(Frame):
            def apply_frame(self, props):
                dx = cx * C[props['i']]
                dy = cy * C[props['i']]

                self.scene.shapes[shape_name].properties['x'] += dx
                self.scene.shapes[shape_name].properties['y'] += dy

                props['i'] += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return scene, dt

    def move_to(self, other_shape, n=None, dt=.01, f=None, shapes=[]):
        ending_point = [
            other_shape.properties['x'],
            other_shape.properties['y']
        ]

        return self.move_to_point(ending_point, n, dt, f, shapes + [other_shape])


