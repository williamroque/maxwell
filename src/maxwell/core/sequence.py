import os

from maxwell.client.message import Message
from maxwell.core.properties import PropertiesEncoder
from maxwell.core.group import Group


class Sequence:
    def __init__(self, client, scenes=None, fps=100, background=None):
        self.client = client

        if scenes is None:
            scenes = []

        self.scenes = scenes

        self.fps = fps

        if background is None:
            background = Group()

        self.background = background

        self.show_shapes = []


    def add_scene(self, scene):
        self.scenes.append(scene)

        for shape in self.show_shapes:
            scene.add_shape(shape)


    def show(self, shape):
        self.show_shapes.append(shape)


    def wait(self, duration):
        if len(self.scenes) > 0:
            self.scenes[-1].extend(int(duration * self.fps))


    def compile(self, save_path='none', initial_clear=True, clears=True):
        save_path = os.path.expanduser(save_path)
        if not os.path.isdir(save_path) and save_path != 'none':
            os.mkdir(save_path)

        rendered_frames = [frame for scene in self.scenes for frame in scene.render_frames()]

        if initial_clear:
            rendered_frames = [[]] + rendered_frames

        message = Message(
            self.client, 'renderScene',
            encoder          = PropertiesEncoder,
            frames           = rendered_frames,
            background       = list(self.background.shapes.values()),
            frameDuration    = 1/self.fps,
            savePath         = save_path,
            framerate        = self.fps,
            fps              = self.fps,
            clears           = clears,
            awaitsCompletion = False,
        )

        return message


    def run(self, **kwargs):
        message = self.compile(**kwargs)
        message.send()
