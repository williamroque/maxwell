from core.util import clear, await_properties

from client.client import Client
from shapes.line import LineSet

import numpy as np


client = Client()

clear(client)

x_scale = 40
y_scale = 40

width, height = await_properties(client, ['width', 'height'])

x_offset = width / 2
y_offset = height / 2

X = np.linspace(-np.pi, np.pi, 100)
Y = np.sin(X)

display = lambda x, y: (x * x_scale + x_offset, -y * y_scale + y_offset)

sin_x = LineSet(client, list(zip(*display(X, Y))), 'orange', 2)
sin_x.render()

y_axis = LineSet(client, [(x_offset, 0), (x_offset, 500)], '#ccc', 1)
y_axis.render()

x_axis = LineSet(client, [(0, y_offset), (600, y_offset)], '#ccc', 1)
x_axis.render()

client.close()
