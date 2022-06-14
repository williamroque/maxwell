from maxwell.core.sequence import Sequence
from maxwell.core.scene import Scene
from maxwell.core.frame import Frame


def apply_universe_frame(self, props):
    for interaction in props.interactions:
        interaction.interact()

    for obj in props.objects:
        obj.apply_properties()


class Universe:
    "A class to store all physically interacting objects in a simulation."

    def __init__(self, client, objects=None):
        "Big bang."

        self.client = client

        self.objects = []
        self.interactions = []

        if objects is None:
            objects = []

        for obj in objects:
            self.add_object(obj)

    def add_object(self, obj):
        "Make sure new object interacts with every existing object and add."

        for other in self.objects:
            self.interactions += obj.create_interactions(other)

        self.objects.append(obj)

    def render(self, duration=10, fps=100, camera=None):
        sequence = Sequence(self.client, None, fps, None, camera)
        frame_num = duration * fps

        scene = Scene(self.client, {
            'objects': self.objects,
            'interactions': self.interactions
        })

        for obj in self.objects:
            scene.add_shape(obj.figure)
