from time import sleep
import os

import functools

import numpy as np
from math import factorial as fact

from maxwell.client.message import Message

import maxwell.core.util as util
from maxwell.core.util import partial, series, taylor, rationalize, complex_split

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
from maxwell.shapes.svg import SVG
from maxwell.shapes.table import Table

from maxwell.core.animation import AnimationConfig, create_easing_function, animate

from maxwell.client.client import Client

from maxwell.core.sequence import Sequence
from maxwell.core.scene import Scene
from maxwell.core.frame import Frame
from maxwell.core.group import Group
from maxwell.core.camera import Camera

from maxwell.core.coordinates.cartesian.system import CartesianSystem, CartesianGridConfig, TRIG, FRACTION
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
    clear_latex = partial(util.clear_latex, client)
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

## Constants
    RED = '#DC5A5E'
    GREEN = '#A6B860'
    BLUE = '#7AA1C0'
    WHITE = '#FDF4C1'
    BLACK = '#121112'

## Convenience functions
    def natural_labels(labels):
        labels = list(labels)

        def x_formatter(x):
            x = float(x)

            if x.is_integer() and 1 <= x <= len(labels):
                return r'\text{{{}}}'.format(labels[int(x) - 1])
            return ''

        def y_formatter(y):
            y = float(y)

            if y.is_integer() and y >= 1:
                return str(int(y))
            return ''

        return CartesianGridConfig(
            x_label_format=x_formatter,
            y_label_format=y_formatter
        )


    def screenshot(render=True, is_temporary=True, clears=False, canvas='pen'):
        image_directory = os.path.expanduser('~/Desktop')
        directory_files = os.listdir(image_directory)
        image_path = os.path.join(
            image_directory,
            next(filter(lambda x: x.endswith('.png'), directory_files))
        )

        image_config = ImageConfig(is_temporary=is_temporary)
        shape_config = ShapeConfig(canvas=canvas)

        point = system.from_normalized(await_click())

        if clears:
            clear()

        image = Image(image_path, point, image_config=image_config, shape_config=shape_config)

        if render:
            image.render()

        return image


    def capture_area(path, background=False):
        message = Message(
            client,
            'captureArea',
            path = os.path.expanduser(path),
            background = background
        )
        message.send()

        return client.receive_message()

## For when the server might not be up
    def run(callback):
        callback()
except ConnectionError:
    def run(_):
        pass

class Composable:
    def __init__(self, func):
        self.func = func
        functools.update_wrapper(self, func)

    def __matmul__(self, other):
        @Composable
        def composition(*args, **kwargs):
            return self.func(other.func(*args, **kwargs))

        return composition

    def __neg__(self):
        @Composable
        def negation(*args, **kwargs):
            return -self.func(*args, **kwargs)

        return negation

    def __add__(self, other):
        @Composable
        def function(*args, **kwargs):
            if isinstance(other, self.__class__):
                return self.func(*args, **kwargs) + other.func(*args, **kwargs)
            return self.func(*args, **kwargs) + other

        return function

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        @Composable
        def function(*args, **kwargs):
            if isinstance(other, self.__class__):
                return self.func(*args, **kwargs) - other.func(*args, **kwargs)
            return self.func(*args, **kwargs) - other

        return function

    def __rsub__(self, other):
        @Composable
        def function(*args, **kwargs):
            return other - self.func(*args, **kwargs)

        return function

    def __mul__(self, other):
        @Composable
        def function(*args, **kwargs):
            if isinstance(other, self.__class__):
                return self.func(*args, **kwargs) * other.func(*args, **kwargs)
            return self.func(*args, **kwargs) * other

        return function

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        @Composable
        def function(*args, **kwargs):
            if isinstance(other, self.__class__):
                return self.func(*args, **kwargs) / other.func(*args, **kwargs)
            return self.func(*args, **kwargs) / other

        return function

    def __rtruediv__(self, other):
        @Composable
        def function(*args, **kwargs):
            return other / self.func(*args, **kwargs)

        return function

    def __pow__(self, other):
        @Composable
        def function(*args, **kwargs):
            if isinstance(other, self.__class__):
                return self.func(*args, **kwargs) ** other.func(*args, **kwargs)
            return self.func(*args, **kwargs) ** other

        return function

    def __rpow__(self, other):
        @Composable
        def function(*args, **kwargs):
            return other ** self.func(*args, **kwargs)

        return function

    __xor__ = __pow__
    __rxor__ = __rpow__

    def __call__(self, *args, **kwargs):
        if len(args) == 1 and isinstance(args[0], self.__class__):
            return self.__matmul__(args[0])
        return self.func(*args, **kwargs)

@Composable
def variable(x):
    return x

x = variable
y = variable
t = variable
n = variable
θ = variable

sin = Composable(np.sin)
cos = Composable(np.cos)
tan = Composable(np.tan)
asin = arcsin = Composable(np.arcsin)
acos = arccos = Composable(np.arccos)
atan = arctan = Composable(np.arctan)
csc = 1/sin
sec = 1/cos
cot = 1/tan
asec = acos @ (1/t)
acsc = asin @ (1/t)
acot = atan @ (1/t)
sqrt = Composable(np.sqrt)
log = ln = Composable(np.log)
pi = π = np.pi

arr = lambda *args: np.array(args)

I = lambda arg: lambda *_, **__: arg
