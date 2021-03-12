import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Text(Shape):
    def __init__(self, client, text, x=0, y=0, font_spec='15pt CMU Serif', color='#fff', stroked=False, system=None, group=None):
        """
        A class for normal text.

        Arguments:
        * client       -- Target client.
        * text         -- The text to be displayed.
        * x            -- The x-coordinate.
        * y            -- The y-coordinate.
        * font_size    -- The font size.
        * color        -- The font color.
        * system       -- The coordinate system.
        * group
        """

        self.client = client
        self.system = system
        self.group = group

        if self.group is not None:
            self.group.add_shape(self)

        self.properties = Properties(
            type = 'text',
            text = text,
            x = x,
            y = y,
            fontSpec = font_spec,
            color = color,
            stroked = stroked
        )

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
