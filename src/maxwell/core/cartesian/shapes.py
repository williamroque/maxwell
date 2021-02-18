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

def create_axes(client, width, height, color='#333D'):
    """
    A function for creating axes. Output may be separated
    into component axes or rendered at the same time.

    Arguments:
    * client -- Target client.
    * width  -- Width of axis. Usually frame width.
    * height -- Height of axis. Usually frame height.
    """

    x_axis = LineSet(client, [(0, height/2), (width, height/2)], width=1, color=color)
    y_axis = LineSet(client, [(width/2, 0), (width/2, height)], width=1, color=color)

    return Axes(x_axis, y_axis)

class Grid():
    def __init__(self, v_lines, h_lines):
        self.v_lines = v_lines
        self.h_lines = h_lines

    def __iter__(self):
        yield self.v_lines
        yield self.h_lines

    def render(self):
        lines = self.v_lines + self.h_lines

        for line in lines:
            line.render()

        return lines

def create_grid(client, system, width, height, n, density, color='#333B'):
    v_lines = []
    h_lines = []

    dx, dy = system.scale / density

    for i in range(-n, n + 1):
        x = system.origin[0] + dx * i
        v_lines.append(LineSet(client, [(x, 0), (x, height)], width=1, color=color))

        y = system.origin[1] + dy * i
        h_lines.append(LineSet(client, [(0, y), (width, y)], width=1, color=color))

    return Grid(v_lines, h_lines)

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
