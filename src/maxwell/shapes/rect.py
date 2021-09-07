import datetime

import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Rect(Shape):
    def __init__(self, client, shape_name=None, x=0, y=0, cx=30, cy=30, fill_color='#fff', border_color='#fff', system=None, group=None):
        """
        A class for rectangles.

        Arguments:
        * client     -- Target client.
        * shape_name
        * x          -- The x-coordinate.
        * y          -- The y-coordinate.
        * cx         -- The width of the rectangle.
        * cy         -- The height of the rectangle.
        * fill_color -- Fill color.
        * border     -- Border color.
        * system     -- The coordinate system.
        * group
        """

        self.client = client
        self.group = group

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        self.shape_name = shape_name

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        self.properties = Properties(
            type = 'rect',
            x = x,
            y = y,
            cx = cx,
            cy = cy,
            fillColor = fill_color,
            borderColor = border_color,
        )

        self.system = system

    def get_props(self, background=False):
        adjustments = {
            'background': background
        }

        if self.system is not None:
            point = self.system.normalize(
                np.array([
                    self.properties.x,
                    self.properties.y
                ])
            ).astype(int).tolist()

            adjustments['x'] = point[0]
            adjustments['y'] = point[1]

        return {
            **self.properties
        } | adjustments

    def render(self, background=False):
        message = {
            'command': 'draw',
            'args': self.get_props(background)
        }

        self.client.send_message(message)

        return self
