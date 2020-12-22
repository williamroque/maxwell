from time import sleep

from core.util import clear, await_event
from core.scene import Scene
from core.frame import Frame

from client.client import Client
from shapes.rect import Rect


client = Client()

scene = Scene('Fantastic scene')

rect = Rect(
    client,
    await_event(client, 'click', ['clientX'])[0], 10,
    100, 100,
    'orange', 'transparent'
)

scene.add_shape(rect, 'orange-rect')

rect.v = [0, 0]
rect.a = [0, 1]


class MoveFrame(Frame):
    def __init__(self):
        super().__init__()

    def apply_frame(self):
        rect = self.scene.shapes['orange-rect']

        if rect.x <= 350:
            rect.x += rect.v[0]

        if rect.y <= 350:
            rect.y += rect.v[1]

        rect.v[0] += rect.a[0]
        rect.v[1] += rect.a[1]


for _ in range(28):
    frame = MoveFrame()
    scene.add_frame(frame)

for _ in scene.frames:
    clear(client, True)
    scene.render()
    scene.next_frame(.05)

sleep(5)

clear(client)

client.close()
