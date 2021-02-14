from mframe.core.util import clear, await_properties
from mframe.shapes.polygon import Polygon

from mframe.core.scene import Scene
from mframe.core.frame import Frame

from client.client import Client

import numpy as np


client = Client()
width, height = await_properties(client, ['width', 'height'])

clear(client)

scene = Scene(client)

side_length = 200
altitude = np.sqrt(side_length ** 2 - (side_length / 2) ** 2)

polygon = Polygon(client, [width/2-side_length/2, height/2+altitude/2], 3, 200, 'orange', 1)
polygon.render()

scene.add_shape(polygon, 'polygon')

class IncreaseNFrame(Frame):
    def __init__(self, index):
        super().__init__()

        self.index = index

    def apply_frame(self, properties):
        self.scene.shapes['polygon'].change_side_number(self.index + 3)

for i in range(30):
    frame = IncreaseNFrame(i)
    scene.add_frame(frame)

scene.play(frame_duration=1)

client.close()
