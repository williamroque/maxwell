import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Rect(Shape):
    def __init__(self, client, x=0, y=0, cx=30, cy=30, fill_color="#fff", border_color="#fff", system=None):
        """
        A class for rectangles.

        Arguments:
        * client     -- Target client.
        * x          -- The x-coordinate.
        * y          -- The y-coordinate.
        * cx         -- The width of the rectangle.
        * cy         -- The height of the rectangle.
        * fill_color -- Fill color.
        * border     -- Border color.
        * system     -- The coordinate system.
        """

        self.client = client

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
