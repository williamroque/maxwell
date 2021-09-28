"For all the shapes related to the cartesian coordinate system."

import numpy as np

from maxwell.shapes.curve import Curve
from maxwell.shapes.text import Text
from maxwell.core.group import Group


class Axes(Group):
    "Main axes for cartesian coordinates."

    def __init__(self, client, **kwargs):
        canvas_shape = client.get_shape()
        x_center, y_center = canvas_shape / 2
        width, height = canvas_shape

        x_axis = Curve(client, [(0, y_center), (width, y_center)], **kwargs)
        y_axis = Curve(client, [(x_center, 0), (x_center, height)], **kwargs)

        super().__init__(shapes=[x_axis, y_axis], background=True)


class Grid():
    def __init__(self, lines):
        self.lines = lines

    def __iter__(self):
        for line in self.lines:
            yield line

    def render(self):
        for line in self.lines:
            line.render()

        return self.lines


def create_grid(client, n, density, color='#333B', width=2, show_numbers=False):
    line_width = width

    width, height = client.get_shape()

    width = int(width)
    height = int(height)

    left_top = system.from_normalized(np.array([0, 0]))
    right_bottom = system.from_normalized(np.array([width, height]))

    lines = []
    numbers = []

    dx = dy = 1 / density

    for i in range(-n, n + 1):
        x = dx * i
        lines.append(Curve(client, [(x, left_top[1]), (x, right_bottom[1])], width=line_width, color=color, system=system))

        y = dy * i
        lines.append(Curve(client, [(left_top[0], y), (right_bottom[0], y)], width=line_width, color=color, system=system))

        if show_numbers:
            font_color = '#57706E'
            font_size = int(system.scale[0] / 6)

            x_margin = system.scale[0] * .0015
            y_margin = system.scale[0] * .0035

            x_label = Text(client, x, x + x_margin, -y_margin, system=system, color=font_color, font_size=font_size)
            y_label = Text(client, y, x_margin, y - y_margin, system=system, color=font_color, font_size=font_size)

            numbers.append(x_label)
            numbers.append(y_label)

    return Grid(lines + numbers)
