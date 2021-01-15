import numpy as np

from mframe.shapes.line import LineSet
from mframe.shapes.rect import Rect
from mframe.client.client import Client
from mframe.core.util import clear, await_properties
from mframe.shapes.latex import Latex
from mframe.core.scene import Scene
from mframe.core.frame import Frame


client = Client()
clear(client)

width, height = await_properties(client, ['width', 'height'])

scene = Scene()

point = np.array([width / 2, height / 2 - 150])

rect = Rect(client, *point, 50, 50, '#ccc', 'transparent')
rect.render()

line_points = [(50, 50), (50, height - 50)]

line = LineSet(client, line_points, color='orange', width=1)
line.render()

scene.add_shape(rect, 'rect')
scene.add_shape(line, 'line')

v = -2
a = -.8
class MotionFrame(Frame):
    def __init__(self):
        super().__init__()

    def apply_frame(self, properties):
        global v, a
        if not LineSet.collide(line_points, point, 5):
            point[0] += v
            self.scene.shapes['rect'].x += v

            v += a
        
for i in range(25):
    scene.add_frame(MotionFrame())

scene.play(client, frame_duration=.05, clear_opacity=.3)
