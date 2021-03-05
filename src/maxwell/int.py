import numpy as np
#import matplotlib.pyplot as plt

import maxwell.core.util as util
from maxwell.core.util import partial, rotate

import maxwell.shapes.arc as arc
import maxwell.shapes.img as img
import maxwell.shapes.latex as latex
import maxwell.shapes.line as line
import maxwell.shapes.polygon as polygon
import maxwell.shapes.rect as rect

from maxwell.client.client import Client

import maxwell.core.scene as scene
from maxwell.core.frame import Frame
from maxwell.core.group import Group

import maxwell.core.cartesian.shapes as shapes
from maxwell.core.cartesian.transformations import System

## Setup

client = Client()

width, height = util.await_properties(client, ['width', 'height'])

scale = np.array([80, 80])
origin = np.array([width / 2, height / 2])
system = System(client, scale, origin)

## client/system currying

clear = partial(util.clear, client)
await_event = partial(util.await_event, client)
await_properties = partial(util.await_properties, client)
await_space = partial(util.await_space, client)
await_click = partial(util.await_click, client)
await_completion = partial(util.await_completion, client)
center_origin = partial(util.center_origin, client, system)
toggle_background = partial(util.toggle_background, client)
set_light_mode = partial(util.set_light_mode, client)
set_dark_mode = partial(util.set_dark_mode, client)
resize_window = partial(util.resize_window, client, system=system)
track_clicks = partial(util.track_clicks, client, system=system)

Arc = partial(arc.Arc, client, system=system)
Image = partial(img.Image, client)
Latex = partial(latex.Latex, client)
LineSet = partial(line.LineSet, client, system=system)
Polygon = partial(polygon.Polygon, client, system=system)
Rect = partial(rect.Rect, client, system=system)

Scene = partial(scene.Scene, client)

create_axes = partial(shapes.create_axes, client, system)
create_grid = partial(shapes.create_grid, client, system)
create_rect = partial(shapes.create_rect, client, system)

## Constants
class COLORS:
    RED = '#DC5A5E'
    GREEN = '#A6B860'
    BLUE = '#7AA1C0'

## Frequently used groups
### Primary/secondary axis group
ps_axis_group = lambda n: Group(shapes={
    'axes': create_axes(),
    'primary-grid': create_grid(n, 1),
    'secondary-grid': create_grid(n * 2, 2)
}, background=True)
