import numpy as np

from maxwell.shapes.line import LineSet
from maxwell.shapes.rect import Rect


class Axes():
    def __init__(self, x_axis, y_axis):
        self.x_axis = x_axis
        self.y_axis = y_axis

    def __iter__(self):
        yield self.x_axis
        yield self.y_axis

    def render(self):
        self.x_axis.render()
        self.y_axis.render()

        return self.x_axis, self.y_axis

def create_axes(client, system, color='#555', width=1):
    """
    A function for creating axes. Output may be separated
    into component axes or rendered at the same time.

    Arguments:
    * client -- Target client.
    * system -- The coordinate system.
    * color  -- The color of the axes.
    """

    line_width = width

    width, height = client.get_shape()
    width = int(width)
    height = int(height)

    x_axis = LineSet(client, [(0, height/2), (width, height/2)], width=line_width, color=color)
    y_axis = LineSet(client, [(width/2, 0), (width/2, height)], width=line_width, color=color)

    return Axes(x_axis, y_axis)

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

def create_grid(client, system, n, density, color='#333B', width=2):
    line_width = width

    width, height = client.get_shape()
    width = int(width)
    height = int(height)

    lines = []

    dx, dy = system.scale / density

    for i in range(-n, n + 1):
        x = system.origin[0] + dx * i
        lines.append(LineSet(client, [(x, 0), (x, height)], width=line_width, color=color))

        y = system.origin[1] + dy * i
        lines.append(LineSet(client, [(0, y), (width, y)], width=line_width, color=color))

    return Grid(lines)

def create_rect(client, system, a, b, h):
    """
    A function for creating a rectangle within a cartesian
    coordinate system. Plays well with Riemann sum
    demonstrations.

    Arguments:
    * client -- Target client.
    * system -- The coordinate system (cartesian).
    * a      -- The starting point.
    * b      -- The end point.
    * h      -- The height of the rectangle.
    """

    rect_width = system.normalize(np.array([b - a, 0]))[0] - system.origin[0]
    rect_height = system.normalize(np.array([0, h]))[1] - system.origin[1]
    x = system.normalize(np.array([a, 0]))[0]
    y = system.origin[1] - h

    rect = Rect(
        client, x, y,
        rect_width, rect_height,
        fill_color='#3332', border_color='#ccc9'
    )

    return rect
