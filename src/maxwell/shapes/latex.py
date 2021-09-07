import datetime
import os

from sympy import preview
import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


def render_latex(latex, src, color):
    preview(
        latex,
        viewer='file',
        filename=src,
        euler=False,
        dvioptions=[
            "-T", "tight", "-z", "0", "--truecolor", "-D 600",
            "-bg", "Transparent", "-fg",
            'rgb {} {} {}'.format(
                color[0] / 255,
                color[1] / 255,
                color[2] / 255,
            )
        ]
    )


class LatexProperties(Properties):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key == 'text':
                self._text = value
            else:
                setattr(self, key, value)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, string):
        self._text = string

        if self.isTemporary:
            self.src = f'/tmp/{datetime.datetime.now()}.png'

        render_latex(
            self._text,
            self.src,
            self.color
        )


class Latex(Shape):
    def __init__(self, client, text, shape_name=None, font_size=12, x=0, y=0, color=(255, 255, 255), path=None, system=None, group=None):
        """
        A class for latex.

        Arguments:
        * client    -- Target client.
        * text      -- The latex to be rendered.
        * shape_name
        * font_size -- Font size in pt.
        * x         -- The display x-coordinate.
        * y         -- The display y-coordinate.
        * color     -- The font color.
        * path      -- The where the rendered latex should be saved. Temporary for None-values.
        * system    -- The coordinate system.
        * group
        """

        self.client = client
        self.system = system
        self.group = group

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        self.shape_name = shape_name

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        if path == None:
            path = f'/tmp/{datetime.datetime.now()}.png'
            is_temporary = True
        else:
            path = os.path.expanduser(path)
            is_temporary = False

        self.properties = LatexProperties(
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
        render_latex(
            self.properties.text,
            self.properties.src,
            self.properties.color
        )

        message = {
            'command': 'draw',
            'args': self.get_props(background)
        }

        self.client.send_message(message)

        return self
