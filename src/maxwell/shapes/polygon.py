import datetime

import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.shapes.line import Curve
from maxwell.core.util import rotate


class Polygon(Shape):
    def __init__(self, client, origin, n_sides, triangle_side_length, shape_name=None, color='#fff', width=3, group=None):
        """
        A class for polygons.

        Arguments:
        * client               -- Target client.
        * origin               -- The starting point for the polygon.
        * n_sides              -- The number of sides of the polygon.
        * triangle_side_length -- The length of the sides if the polygon
        were a triangle.
        * shape_name
        * color                -- The color of the lines.
        * width                -- The stroke width.
        * group
        """

        self.client = client
        self.group = group

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        self.shape_name = shape_name

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        self.origin = origin
        self.triangle_side_length = triangle_side_length
        self.color = color
        self.width = width
        self.points = []

        self.curve = Curve(self.client, np.array(self.points), self.color, self.width)
        self.properties = self.curve.properties

        self.change_side_number(n_sides)

    def change_side_number(self, n):
        self.n_sides = n
        self.side_length = self.triangle_side_length * 3 / self.n_sides

        del self.points[:]

        self.construct_points()

        self.curve.properties.points = np.array(self.points)

    def construct_points(self):
        self.points.append(self.origin)

        d_theta = 180 * (self.n_sides - 2) / self.n_sides
        theta = 0

        point = self.origin

        for _ in range(self.n_sides):
            new_point = [point[0] + self.side_length, point[1]]
            new_point = rotate(np.array(new_point), np.array(point), theta, True)

            self.points.append(new_point)

            theta += 180 + d_theta
            point = new_point

    def render(self, background=False):
        self.curve.render(background)

        return self
