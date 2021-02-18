from maxwell.client.client import Client
from maxwell.core.util import clear, await_properties, await_event, set_dark_mode
from maxwell.shapes.line import LineSet
from maxwell.shapes.latex import Latex
from maxwell.core.scene import Scene
from maxwell.core.frame import Frame
from maxwell.core.cartesian.transformations import System
from maxwell.core.cartesian.shapes import create_axes, create_rect

import numpy as np


## SETUP

client = Client()
scene = Scene(client, {'n': 1})

clear(client)
set_dark_mode(client)

width, height = await_properties(client, ['width', 'height'])

scale = np.array([10, 10]) * 8
origin = np.array([width / 2, height / 2])
system = System(client, scale, origin)

## EQUATION

equation = r'$$\int_a^b f(x) \> dx = \lim_{n \to \infty} \sum^n_{i=1} f(x^*_i) \Delta x$$'
latex = Latex(client, equation, x=30, y=30, font_size=40)
latex.render()

scene.add_shape(latex, 'equation', True)

## GRID

x_axis, y_axis = create_axes(client, width, height)
x_axis.render()
y_axis.render()

## CURVE

f = lambda x: 2*np.sin(x)

X = np.linspace(-4, 4, 1000)
Y = f(X)

points = system.zip_normalize(X, Y)

curve = LineSet(client, points, width=1, color='orange')
curve.render()

## RIEMANN SUM

a = -np.pi
b = np.pi

scene.add_shape(x_axis, 'x-axis', True)
scene.add_shape(y_axis, 'y-axis', True)
scene.add_shape(curve, 'curve', True)

class ApproximationFrame(Frame):
    def apply_frame(self, properties):
        for shape in self.scene.shapes.values():
            if shape.properties.type == 'rect':
                del shape

        dx = (b - a) / properties.n
        for i in range(0, properties.n):
            x_i = a + i*dx

            self.scene.add_shape(create_rect(
                client, system,
                x_i, x_i + dx, f(x_i + dx / 2)
            ), 'rect-' + str(i))

        properties.n += 1

for i in range(30):
    scene.add_frame(ApproximationFrame())

await_event(client, 'click', [])
scene.play(frame_duration=.7)
