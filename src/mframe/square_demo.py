from time import sleep

from core.util import clear, await_event
from core.scene import Scene
from core.frame import Frame

from client.client import Client
from shapes.rect import Rect


client = Client()

scene = Scene('Falling square')

rect = Rect(
    client,
    await_event(client, 'click', ['clientX'])[0], 10,
    100, 100,
    'orange', 'transparent'
)

scene.add_shape(rect, 'orange-rect')

rect.v = [0, 1]
rect.a = [0, 0]


class MoveFrame(Frame):
    def __init__(self):
        super().__init__()

    def apply_frame(self, properties):
        rect = self.scene.shapes['orange-rect']

        if rect.properties['x'] <= 350:
            rect.properties['x'] += rect.v[0]

        if rect.properties['y'] <= 350:
            rect.properties['y'] += rect.v[1]

        rect.v[0] += rect.a[0]
        rect.v[1] += rect.a[1]


for _ in range(350):
    frame = MoveFrame()
    scene.add_frame(frame)

scene.prerender_play(client, frame_duration=.01)

client.close()
