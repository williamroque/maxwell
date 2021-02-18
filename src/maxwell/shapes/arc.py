import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Arc(Shape):
    def __init__(self, client, x=0, y=0, radius=7, theta_1=0, theta_2=2*np.pi, fill_color="#fff", border_color="#fff", system=None):
        """
        A class for arcs.

        Arguments:
        * client       -- Target client.
        * x            -- The x-coordinate.
        * y            -- The y-coordinate.
        * radius       -- The radius of the arc.
        * theta_1      -- The starting angle.
        * theta_2      -- The ending angle.
        * fill_color   -- The fill color for the arc.
        * border_color -- The border color.
        * system       -- The coordinate system.
        """

        self.client = client
        self.system = system

        self.properties = Properties(
            type = 'arc',
            x = x,
            y = y,
            radius = radius,
            theta_1 = theta_1,
            theta_2 = theta_2,
            fillColor = fill_color,
            borderColor = border_color,
        )

    def get_props(self):
        adjustments = {}

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

    def render(self):
        message = {
            'command': 'draw',
            'args': self.get_props()
        }

        self.client.send_message(message)

        return self
