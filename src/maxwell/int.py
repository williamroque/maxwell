import numpy as np
import matplotlib.pyplot as plt

import maxwell.core.util as util
from maxwell.core.util import partial

import maxwell.shapes.arc as arc
import maxwell.shapes.img as img
import maxwell.shapes.latex as latex
import maxwell.shapes.line as line
import maxwell.shapes.polygon as polygon
import maxwell.shapes.rect as rect

from maxwell.client.client import Client

import maxwell.core.scene as scene
from maxwell.core.frame import Frame

import maxwell.core.cartesian.shapes as shapes
from maxwell.core.cartesian.transformations import System

client = Client()

width, height = util.await_properties(client, ['width', 'height'])

scale = np.array([10, 10]) * 8
origin = np.array([width / 2, height / 2])
system = System(scale, origin)

clear = partial(util.clear, client)
await_event = partial(util.await_event, client)
await_properties = partial(util.await_properties, client)
await_space = partial(util.await_space, client)
await_click = partial(util.await_click, client)
center_origin = partial(util.center_origin, client, system)
toggle_background = partial(util.toggle_background, client)
set_light_mode = partial(util.set_light_mode, client)
set_dark_mode = partial(util.set_dark_mode, client)
resize_window = partial(util.resize_window, client)

Arc = partial(arc.Arc, client)
Image = partial(img.Image, client)
Latex = partial(latex.Latex, client)
LineSet = partial(line.LineSet, client)
Polygon = partial(polygon.Polygon, client)
Rect = partial(rect.Rect, client)

Scene = partial(scene.Scene, client)

create_axes = partial(shapes.create_axes, client, width, height)
create_rect = partial(shapes.create_rect, client, system)
