from core.util import clear, await_properties

from client.client import Client
from shapes.arc import Arc
from shapes.line import LineSet

import numpy as np


client = Client()

clear(client)

width, height = await_properties(client, ['width', 'height'])

x_axis = LineSet(client, [(0, height / 2), (width, height / 2)], '#ccc', 1)
x_axis.render()

y_axis = LineSet(client, [(width / 2, 0), (width / 2, height)], '#ccc', 1)
y_axis.render()

circle = Arc(client, width / 2, height / 2, 50, 0, 2 * np.pi, 'transparent', 'orange')
circle.render()

client.close()
