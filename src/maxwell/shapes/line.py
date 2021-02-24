import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties
from maxwell.core.scene import Scene, TransformationScene
from maxwell.core.frame import Frame
from maxwell.core.util import rotate

import datetime


class LineSetProperties(Properties):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._x, self._y = self.points[0] if len(self.points) > 0 else None, None

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value

        dx = value - self.points[0][0]
        for point in self.points:
            point[0] += dx

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value

        dy = value - self.points[0][1]
        for point in self.points:
            point[1] += dy


class LineSet(Shape):
    def __init__(self, client, points, color='#fff', width=3, arrows=0, arrow_size=6, system=None):
        """
        A class for lines.

        Arguments:
        * client     -- Target client.
        * points     -- The points connecting the lines as 2-tuples or
        2-item lists
        * color      -- The color of the lines.
        * width      -- The stroke width of the lines.
        * arrows     -- Which arrows to display if only single line:
        0 = none
        1 = ending point
        2 = starting point
        3 = both
        * arrow_size -- The radius of the circle in which the arrow head
        is inscribed.
        * system     -- The coordinate system.
        """

        self.client = client
        self.system = system

        self.properties = LineSetProperties(
            type = 'lineset',
            points = list(map(list, list(points))),
            color = color,
            width = width,
            arrows = arrows,
            arrowSize = arrow_size
        )

    def get_props(self, background=False):
        adjustments = {
            'background': background
        }

        if self.system is not None:
            adjustments['points'] = self.system.normalize(
                self.properties.points
            ).astype(int).tolist()

        return {
            **self.properties
        } | adjustments

    @staticmethod
    def collide(line, point, threshold=0):
        """
        Determine whether a point coincides with line within a certain
        threshold. This is done by converting to polar coordinates.

        Arguments:
        * line      -- The 2-tuple of 2-tuples (or lists) representing
        the line.
        * point     -- The point.
        * threshold -- The maximum distance between the line and the
        point before they are considered to have collided.
        """

        if point[0] == line[0][0] and point[1] == line[0][1] or\
           point[0] == line[1][0] and point[1] == line[1][1]:
            return True

        line_angle = LineSet.get_angle(*line)
        line_point_angle = LineSet.get_angle(line[0], point)

        line_r = np.sqrt((line[1][0] - line[0][0]) ** 2 + (line[1][1] - line[0][0]) ** 2)
        line_point_r = np.sqrt((line[0][0] - point[0]) ** 2 + (line[0][1] - point[1]) ** 2)

        return round(line_point_r * np.sin(np.abs(line_angle - line_point_angle)), 5) <= threshold and line_point_r <= line_r

    @staticmethod
    def get_angle(p_1, p_2):
        """
        The angular distance between two points, taken as follows:

        │  │
        │  o
        │ ╱│
        │╱ │
        o  │
        │  │

        Arguments:
        * line      -- The 2-tuple of 2-tuples (or lists) representing
        the line.
        * point     -- The point.
        * threshold -- The maximum distance between the line and the
        point before they are considered to have collided.
        """

        dx = p_2[0] - p_1[0]
        dy = p_2[1] - p_1[1]
        r = np.sqrt(dx**2 + dy**2)

        angle = np.arcsin(dy/r)

        if p_2[0] < p_1[0]:
            angle = np.pi - angle

        return angle

    def move_point(self, point_i, ending_point, n=None, dt=.01, f=None, duration=.5, shapes=[]):
        scene = Scene(self.client, { 'i': 0 })

        shape_name = f'{datetime.datetime.now()}-shape'
        scene.add_shape(self, shape_name)

        scene.add_background(shapes)

        cx = ending_point[0] - self.properties.points[point_i][0]
        cy = ending_point[1] - self.properties.points[point_i][1]
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

                self.props(shape_name).points[point_i][0] += dx
                self.props(shape_name).points[point_i][1] += dy

                props.i += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return TransformationScene(scene, dt)

    def follow_path(self, point_i, p, n=500, dt=.01, shapes=[]):
        scene = Scene(self.client, { 'i': 0 })

        shape_name = f'{datetime.datetime.now()}-shape'
        scene.add_shape(self, shape_name)

        scene.add_background(shapes)

        class MotionFrame(Frame):
            def apply_frame(self, props):
                x, y = p(props.i * dt, props.i)

                self.props(shape_name).points[point_i][0] = x
                self.props(shape_name).points[point_i][1] = y

                props.i += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return TransformationScene(scene, dt)

    def rotate_about(self, origin, theta, dt=.01, n=None, n_scale=1, f=None, animate=True, shapes=[]):
        if not animate:
            self.properties.points = rotate(self.properties.points, origin, theta)

            return self

        scene = Scene(self.client, { 'i': 0 })

        shape_name = f'{datetime.datetime.now()}-shape'
        scene.add_shape(self, shape_name)

        scene.add_background(shapes)

        if n is None:
            n = int(abs(theta) * 100 * n_scale)

        if f is None:
            f = (lambda x: 0 * x + 1 / n, 0, 1)

        X = np.linspace(f[1], f[2], n)
        Y = np.abs(f[0](X))
        C = Y / Y.sum()

        class MotionFrame(Frame):
            def apply_frame(self, props):
                d_theta = C[props.i]

                self.props(shape_name).points = rotate(
                    self.props(shape_name).points,
                    origin,
                    d_theta
                )

                props.i += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return TransformationScene(scene, dt)

    def render(self, background=False):
        message = {
            'command': 'draw',
            'args': self.get_props(background)
        }

        self.client.send_message(message, True)

        return self
