import datetime

import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Text(Shape):
    def __init__(self, client, text, x=0, y=0, shape_name=None, font_size='15pt', font_family='CMU Serif', italic=False, markdown=False, color='#fff', stroked=False, system=None, group=None):
        "A class for normal text."

        self.client = client
        self.system = system
        self.group = group

        self.access_hooks = []

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        font_spec = ''

        if italic:
            font_spec += 'italic '

        font_spec += str(font_size) + ' '
        font_spec += font_family

        self.shape_name = shape_name

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        self.properties = Properties(
            type = 'text',
            text = text,
            x = x,
            y = y,
            fontSpec = font_spec,
            color = color,
            stroked = stroked,
            markdown = markdown
        )


    def add_access_hook(self, callback, *args):
        self.access_hooks.append((callback, args))


    def get_props(self, background=False):
        adjustments = {
            'background': background
        }

        for access_hook, args in self.access_hooks:
            access_hook(self, *args)

        if self.system is not None:
            point = self.system.normalize(
                np.array([
                    self.properties.x,
                    self.properties.y
                ])
            ).tolist()

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
