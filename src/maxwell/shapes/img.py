import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Image(Shape):
    def __init__(self, client, src, x, y, width, height, system=None):
        """
        A class for images.

        Arguments:
        * client -- Target client.
        * src    -- The image file's path.
        * x      -- The x-coordinate.
        * y      -- The y-coordinate.
        * width  -- The image's display width.
        * height -- The image's display height.
        * system -- The coordinate system.
        """

        self.client = client

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
