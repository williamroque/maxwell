import numpy as np
import matplotlib.pyplot as plt

import inspect

import mframe.core.util as util

import mframe.shapes.arc as arc
import mframe.shapes.img as img
import mframe.shapes.latex as latex
import mframe.shapes.line as line
import mframe.shapes.polygon as polygon
import mframe.shapes.rect as rect

from mframe.client.client import Client

import mframe.core.scene as scene
from mframe.core.frame import Frame

import mframe.core.cartesian.shapes as shapes
from mframe.core.cartesian.transformations import System

client = Client()

width, height = util.await_properties(client, ['width', 'height'])

scale = np.array([10, 10]) * 8
origin = np.array([width / 2, height / 2])
system = System(scale, origin)

def partial(func, *partial_args, **partial_kwargs):
    partial_func = lambda *args, **kwargs: func(*partial_args, *args, **partial_kwargs, **kwargs)
    partial_func.__doc__ = func.__doc__

    if inspect.isclass(func):
        partial_func.__doc__ = func.__init__.__doc__

    return partial_func

clear = partial(util.clear, client)
await_event = partial(util.await_event, client)
await_properties = partial(util.await_properties, client)

Arc = partial(arc.Arc, client)
Image = partial(img.Image, client)
Latex = partial(latex.Latex, client)
LineSet = partial(line.LineSet, client)
Polygon = partial(polygon.Polygon, client)
Rect = partial(rect.Rect, client)

Scene = partial(scene.Scene, client)

create_axes = partial(shapes.create_axes, client, width, height)
create_rect = partial(shapes.create_rect, client, system)
