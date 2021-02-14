import numpy as np

from mframe.shapes.line import LineSet
from mframe.shapes.rect import Rect
from mframe.client.client import Client
from mframe.core.util import clear, await_properties, await_event
from mframe.shapes.latex import Latex
from mframe.core.scene import Scene
from mframe.core.frame import Frame


client = Client()
clear(client)

width, height = await_properties(client, ['width', 'height'])

scene = Scene(client)

point = np.array([width / 2, height / 2 - 150])

rect = Rect(client, *point, 50, 50, 'transparent', '#ccc')
rect.render()

line_points = [(100, 50), (50, height - 50)]

line = LineSet(client, line_points, color='orange', width=1)
line.render()

scene.add_shape(rect, 'rect')
scene.add_shape(line, 'line')

dt = .01

v = -300
a = 0
class MotionFrame(Frame):
    def __init__(self):
        super().__init__()

    def apply_frame(self, properties):
        global v, a
        if not LineSet.collide(line_points, point, 1):
            point[0] += v * dt
            self.scene.shapes['rect'].properties['x'] += v * dt

            v += a * dt
        
for i in range(110):
    scene.add_frame(MotionFrame())

await_event(client, 'click')

scene.play(frame_duration=dt)
