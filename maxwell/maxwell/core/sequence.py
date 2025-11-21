import os

from maxwell.client.message import Message
from maxwell.core.properties import PropertiesEncoder
from maxwell.core.group import Group


class Sequence:
    def __init__(self, client, scenes=None, fps=100, background=None, camera=None):
        self.client = client

        if scenes is None:
            scenes = []

        self.scenes = scenes

        self.fps = fps

        if background is None:
            background = Group()

        self.background = background
        self.camera = camera

        self.show_shapes = []


    def add_scene(self, scene):
        if scene.camera is None:
            scene.camera = self.camera

        self.scenes.append(scene)

        for shape in self.show_shapes:
            scene.add_shape(shape)


    def add_scenes(self, first, *rest):
        for scene in rest:
            first.link_scene(scene)

        self.add_scene(first)


    def show(self, shape):
        if isinstance(shape, Group):
            for member in shape.shapes.values():
                self.show(member)
        else:
            self.show_shapes.append(shape)


    def wait(self, duration):
        frame_num = int(duration * self.fps)

        if len(self.scenes) > 0:
            self.scenes[-1].extend(frame_num)
        else:
            from maxwell.core.scene import Scene

            scene = Scene(self.client, {}, self.camera)

            for shape in self.show_shapes:
                scene.add_shape(shape)

            scene.repeat_frame(frame_num)

            self.scenes.append(scene)


    def compile(self, save_path='none', initial_clear=True, clears=True, await_completion=False):
        save_path = os.path.expanduser(save_path)

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
            awaitsCompletion = await_completion,
        )

        return message


    def run(self, **kwargs):
        message = self.compile(**kwargs)
        message.send()
