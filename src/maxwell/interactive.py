from time import sleep

import numpy as np

import maxwell.core.util as util
from maxwell.core.util import partial

import maxwell.shapes.arc as arc
import maxwell.shapes.img as img
import maxwell.shapes.latex as latex
import maxwell.shapes.line as line
import maxwell.shapes.polygon as polygon
import maxwell.shapes.rect as rect
import maxwell.shapes.text as text
import maxwell.shapes.vector as vector
import maxwell.shapes.measure as measure

from maxwell.client.client import Client

from maxwell.core.sequence import Sequence
import maxwell.core.scene as scene
from maxwell.core.frame import Frame
from maxwell.core.group import Group
from maxwell.core.camera import Camera

import maxwell.core.cartesian.shapes as shapes
from maxwell.core.cartesian.system import System

try:
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
    set_background = partial(util.set_background, client)
    set_light_mode = partial(util.set_light_mode, client)
    set_dark_mode = partial(util.set_dark_mode, client)
    resize_window = partial(util.resize_window, client, system=system)
    track_clicks = partial(util.track_clicks, client, system=system)

    global_group = Group()

    zip_function = line.Curve.zip_function
    zip_functions = line.Curve.zip_functions

    Arc = partial(arc.Arc, client, system=system, group=global_group)
    Image = partial(img.Image, client, group=global_group)
    Latex = partial(latex.Latex, client, group=global_group)
    Curve = LS = partial(line.Curve, client, system=system, group=global_group)
    Polygon = partial(polygon.Polygon, client, system=system, group=global_group)
    Rect = partial(rect.Rect, client, system=system, group=global_group)
    Text = partial(text.Text, client, system=system, group=global_group)
    Vector = partial(vector.Vector, client, system=system, group=global_group)
    Measure = partial(measure.Measure, client, system=system, group=global_group)

    Scene = partial(scene.Scene, client)

    Sequence = partial(Sequence, client)
    Camera = partial(Camera, client)

    create_axes = partial(shapes.create_axes, client, system)
    create_grid = partial(shapes.create_grid, client, system)
    create_rect = partial(shapes.create_rect, client, system)
    create_vector_field = partial(vector.create_vector_field, client, system=system)

## Constants
    RED = '#DC5A5E'
    GREEN = '#A6B860'
    BLUE = '#7AA1C0'

## Frequently used groups
### Primary/secondary axis group
    ps_axis_group = lambda n, primary_width=2, show_numbers=False: Group(shapes=[
        create_grid(n, 1, width=primary_width, show_numbers=show_numbers),
        create_grid(n * 2, 2, width=1),
        create_axes(width=1),
    ], background=True)

## For quick graphing
    def init_graph(scale_by=1.0, n=5, show_numbers=False):
        clear()

        system.scale *= scale_by
        ps_axis_group(n, show_numbers=show_numbers).render()

## For when the server might not be up
    def run(callback):
        callback()
except ConnectionError:
    def run(_):
        pass
