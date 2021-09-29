from time import sleep

import numpy as np

import maxwell.core.util as util
from maxwell.core.util import partial

from dataclasses import replace

from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.measure import Measure, MeasureConfig
from maxwell.shapes.text import Text, TextConfig
from maxwell.shapes.vector import Vector, create_vector_field
from maxwell.shapes.arc import Arc, ArcConfig
from maxwell.shapes.latex import Latex, LatexConfig
from maxwell.shapes.image import Image, ImageConfig
from maxwell.shapes.rect import Rect, RectConfig

from maxwell.core.animation import AnimationConfig, create_easing_function, animate

from maxwell.client.client import Client

from maxwell.core.sequence import Sequence
from maxwell.core.scene import Scene
from maxwell.core.frame import Frame
from maxwell.core.group import Group
from maxwell.core.camera import Camera

from maxwell.core.coordinates.cartesian.system import CartesianSystem, CartesianGridConfig, TRIG_CONFIG
from maxwell.core.coordinates.polar.system import PolarSystem, PolarGridConfig
from maxwell.core.coordinates.system import System

try:
## Setup

    client = Client()

    width, height = util.await_properties(client, ['width', 'height'])

    scale = np.array([80.0, 80.0])
    origin = np.array([width / 2, height / 2])

    System.DEFAULT_CLIENT = client

    system = CartesianSystem(client, scale, origin)
    canvas_system = System(client)
    polar_system = PolarSystem(client, scale, origin)

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

    Shape.DEFAULT_CLIENT = client
    Shape.DEFAULT_SYSTEM = system

    Scene.DEFAULT_CLIENT = client

    Sequence = partial(Sequence, client)
    Camera = partial(Camera, client)

    clear()

## Constants
    RED = '#DC5A5E'
    GREEN = '#A6B860'
    BLUE = '#7AA1C0'

## For when the server might not be up
    def run(callback):
        callback()
except ConnectionError:
    def run(_):
        pass
