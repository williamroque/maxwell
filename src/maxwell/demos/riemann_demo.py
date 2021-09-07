from maxwell.int import *

import numpy as np


## SETUP

scene = Scene({'n': 1})

clear()
set_dark_mode()

## EQUATION

equation = r'$$\int_a^b f(x) \> dx = \lim_{n \to \infty} \sum^n_{i=1} f(x^*_i) \Delta x$$'
latex = Latex(equation, x=30, y=30, font_size=40).render()

scene.add_shape(latex, 'equation', True)

## GRID

x_axis, y_axis = create_axes().render()

## CURVE

f = lambda x: 2*np.sin(x)

X = np.linspace(-4, 4, 1000)
Y = f(X)

curve = LineSet(zip(X, Y), width=1, color='orange').render()

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
                x_i, x_i + dx, f(x_i + dx / 2)
            ), 'rect-' + str(i))

        properties.n += 1

for i in range(30):
    scene.add_frame(ApproximationFrame())

await_space()
scene.play(frame_duration=.7)
