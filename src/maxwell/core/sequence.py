import os
import json

from maxwell.client.message import Message
from maxwell.core.properties import PropertiesEncoder


class Sequence:
    def __init__(self, client, scenes=None, fps=100, background=None):
        self.client = client

        if scenes is None:
            scenes = []

        self.scenes = scenes

        self.fps = fps

        if background is None:
            background = {}

        self.background = background


    def add_scene(self, scene):
        self.scenes.append(scene)


    def wait(self, duration):
        self.scenes[-1].extend(duration*self.fps)


    def get_background_props(self):
        return [shape.get_props() for shape in self.background.values()]


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
            background       = self.get_background_props(),
            frameDuration    = 1/self.fps,
            savePath         = save_path,
            framerate        = self.fps,
            fps              = self.fps,
            clears           = clears,
            awaitsCompletion = False,
        )

        return message

