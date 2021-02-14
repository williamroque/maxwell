from mframe.client.client import Client
from mframe.core.util import clear, await_properties, await_event
from mframe.shapes.line import LineSet
from mframe.shapes.latex import Latex
from mframe.core.scene import Scene
from mframe.core.frame import Frame
from mframe.core.cartesian.transformations import System
from mframe.core.cartesian.shapes import create_axes, create_rect

import numpy as np

client = Client()
clear(client)

width, height = await_properties(client, ['width', 'height'])

scale = np.array([10, 10]) * 8
origin = np.array([width / 2, height / 2])
system = System(scale, origin)

## EQUATION

equation = r'$$\int_a^b f(x) \> dx = \lim_{n \to \infty} \sum^n_{i=1} f(x^*_i) \Delta x$$'
latex = Latex(client, equation, x=-50, y=0, scale=110)
latex.render()

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

scene = Scene(client, {'n': 1})
scene.add_shape(x_axis, 'x-axis')
scene.add_shape(y_axis, 'y-axis')
scene.add_shape(curve, 'curve')

class ApproximationFrame(Frame):
    def apply_frame(self, properties):
        for shape in self.scene.shapes.values():
            if shape.properties['type'] == 'rect':
                del shape

        dx = (b - a) / properties['n']
        for i in range(0, properties['n']):
            x_i = a + i*dx

            self.scene.add_shape(create_rect(
                client, system,
                x_i, x_i + dx, f(x_i + dx / 2)
            ), 'rect-' + str(i))

        properties['n'] += 1

for i in range(30):
    scene.add_frame(ApproximationFrame())

await_event(client, 'click', [])
scene.play(frame_duration=.7)
