import numpy as np

from mframe.shapes.shape import Shape
from mframe.core.properties import Properties


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
    def __init__(self, client, points, color='#fff', width=3, arrows=0, arrow_size=6):
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
        """

        self.client = client

        self.properties = LineSetProperties(
            type = 'lineset',
            points = list(map(list, points)),
            color = color,
            width = width,
            arrows = arrows,
            arrowSize = arrow_size
        )

    @staticmethod
    def rotate(origin, point, theta, degrees=False):
        """
        Rotate a point about an arbitrary origin.

        Arguments:
        * origin -- The origin.
        * point -- The point to be rotated.
        * theta -- The angle of rotation.
        * degrees -- Whether the angle should be in degrees
        (radians by default).
        """

        if degrees:
            theta = theta * np.pi / 180

        theta = LineSet.get_angle(origin, point) + theta

        dx = point[0] - origin[0]
        dy = point[1] - origin[1]

        r = np.sqrt(dx ** 2 + dy ** 2)
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        point[0] = x + origin[0]
        point[1] = -y + origin[1]

        return point

    def translate_all(self, dx=0, dy=0):
        """
        Translate all endpoints with respect to x and y components.

        Arguments:
        * dx -- The amount by which the x-component should change.
        * dy -- The amount by which the y-component should change.
        """

        for point in self.properties['points']:
            point[0] += dx
            point[1] += dy

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

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)
