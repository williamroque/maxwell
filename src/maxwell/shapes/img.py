import datetime

import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Image(Shape):
    def __init__(self, client, src, x, y, width, height, shape_name=None, system=None, group=None):
        """
        A class for images.

        Arguments:
        * client     -- Target client.
        * shape_name
        * src        -- The image file's path.
        * x          -- The x-coordinate.
        * y          -- The y-coordinate.
        * width      -- The image's display width.
        * height     -- The image's display height.
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
            type = 'image',
            src = src,
            x = x,
            y = y,
            width = width,
            height = height,
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
