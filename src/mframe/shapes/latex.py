import datetime
import os

from sympy import preview

from mframe.shapes.shape import Shape
from mframe.core.properties import Properties


class Latex(Shape):
    def __init__(self, client, text, font_size=12, x=0, y=0, color=(255, 255, 255), path=None):
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
        """

        self.client = client

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

    def render(self):
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
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)

        return self
