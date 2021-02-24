import datetime
import os

from sympy import preview
import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Latex(Shape):
    def __init__(self, client, text, font_size=12, x=0, y=0, color=(255, 255, 255), path=None, system=None):
        """
        A class for latex.

        Arguments:
        * client    -- Target client.
        * text      -- The latex to be rendered.
        * font_size -- Font size in pt.
        * x         -- The display x-coordinate.
        * y         -- The display y-coordinate.
        * color     -- The font color.
        * path      -- The where the rendered latex should be saved. Temporary for None-values.
        * system    -- The coordinate system.
        """

        self.client = client
        self.system = system

        if path == None:
            path = f'/tmp/{datetime.datetime.now()}.png'
            is_temporary = True
        else:
            path = os.path.expanduser(path)
            is_temporary = False

        self.properties = Properties(
            type = 'image',
            src = path,
            x = x,
            y = y,
            height = (text.count('\n\n') + 1) * font_size * 4/3,
            color = color,
            text = text,
            isTemporary = is_temporary
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
        preview(
            self.properties.text,
            viewer='file',
            filename=self.properties.src,
            euler=False,
            dvioptions=[
                "-T", "tight", "-z", "0", "--truecolor", "-D 600",
                "-bg", "Transparent", "-fg",
                'rgb {} {} {}'.format(
                    self.properties.color[0] / 255,
                    self.properties.color[1] / 255,
                    self.properties.color[2] / 255,
                )
            ]
        )

        message = {
            'command': 'draw',
            'args': self.get_props(background)
        }

        self.client.send_message(message)

        return self
