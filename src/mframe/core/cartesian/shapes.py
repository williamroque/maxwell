import numpy as np

from mframe.shapes.line import LineSet
from mframe.shapes.rect import Rect


def create_axes(client, width, height):
    x_axis = LineSet(client, [(0, height/2), (width, height/2)], width=1, color='#333D')
    y_axis = LineSet(client, [(width/2, 0), (width/2, height)], width=1, color='#333D')

    return x_axis, y_axis

def create_rect(client, system, a, b, h):
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
