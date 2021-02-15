from mframe.core.util import clear, await_event
from mframe.core.scene import Scene
from mframe.core.frame import Frame

from client.client import Client
from shapes.rect import Rect


client = Client()

clear(client)

await_event(client, 'click', [])

scene = Scene(client)

rect = Rect(
    client,
    50, 10,
    100, 100,
    '#ccc', 'transparent'
)

scene.add_shape(rect, 'orange-rect')

rect.v = [0, 0]
rect.a = [0, 1.5]

dt = .01


class MoveFrame(Frame):
    def __init__(self):
        super().__init__()

    def apply_frame(self, properties):
        rect = self.scene.shapes['orange-rect']

        if rect.properties.x <= 350:
            rect.properties.x += rect.v[0] * dt

        if rect.properties.y <= 350:
            rect.properties.y += rect.v[1] * dt

        rect.v[0] += rect.a[0]
        rect.v[1] += rect.a[1]


for _ in range(500):
    frame = MoveFrame()
    scene.add_frame(frame)

scene.play(save_path='~/Desktop/animation', frame_duration=dt)

client.close()
