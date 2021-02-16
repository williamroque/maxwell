from core.util import clear, await_properties

from client.client import Client
from shapes.img import Image

import matplotlib.pyplot as plt
import datetime
import numpy as np


fig_width = 4
fig_height = 3

plt.style.use('dark_background')
plt.rcParams["figure.figsize"] = (fig_width, fig_height)

client = Client()

clear(client)

width, height = await_properties(client, ['width', 'height'])
src = f'/Users/jetblack/Desktop/{datetime.datetime.now()}.png'

X = np.linspace(-np.pi, np.pi, 100)
Y = np.sin(X)

plt.plot(X, Y)

ax = plt.gca()
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.spines['bottom'].set_position(('data', 0))
ax.yaxis.set_ticks_position('left')
ax.spines['left'].set_position(('data', 0))

plt.savefig(src, transparent=True, dpi=300)

img_scale = 150

img_width = fig_width * img_scale
img_height = fig_height * img_scale

image = Image(
    client,
    src,
    width / 2 - img_width / 2,
    height / 2 - img_height / 2,
    img_width, img_height
)
image.render()

client.close()
