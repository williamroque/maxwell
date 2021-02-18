from time import sleep
import os

import json

from maxwell.core.util import clear, download_canvas
from maxwell.core.properties import PropertiesEncoder, Properties


class Scene():
    def __init__(self, client, properties={}):
        self.frames = []
        self.current_frame = -1

        self.properties = Properties(**properties)
        self.merged_properties = []

        self.shapes = {}
        self.background = {}

        self.client = client

    def add_frame(self, frame):
        self.current_frame = 0

        frame.set_scene(self)
        self.frames.append([frame])

    def next_frame(self, timeout=0):
        self.current_frame += 1
        sleep(timeout)

    def add_shape(self, shape, shape_id, send_to_background=False):
        if send_to_background:
            self.background[shape_id] = shape
        else:
            self.shapes[shape_id] = shape

    def merge_with(self, other_scene):
        self.merged_properties.append(other_scene.properties)
        self.shapes |= other_scene.shapes

        for i, frames in enumerate(other_scene.frames):
            for frame in frames:
                frame.set_scene(self)

            if i < len(self.frames):
                self.frames[i] += frames
            else:
                self.frames.append(frames)

        return self

    def play(self, frame_duration=.05, save_path='none', framerate=40, fps=40):
        rendered_frames = [json.dumps(self.shapes, cls=PropertiesEncoder)]
        for frames in self.frames:
            for i, frame in enumerate(frames):
                frame.apply_frame(self.merged_properties[i - 1] if i > 0 else self.properties)
            rendered_frames.append(json.dumps(self.shapes, cls=PropertiesEncoder))

        message = {
            'command': 'renderScene',
            'args': {
                'frames': rendered_frames,
                'background': json.dumps(self.background, cls=PropertiesEncoder),
                'frameDuration': frame_duration,
                'savePath': os.path.expanduser(save_path),
                'framerate': framerate,
                'fps': fps,
            }
        }

        self.client.send_message(message)

    def render(self):
        if self.current_frame > -1:
            self.frames[self.current_frame].apply_frame(self.properties)
            for shape in self.shapes.values():
                shape.render()


class TransformationScene:
    def __init__(self, scene, dt):
        self.scene = scene
        self.dt = dt

    def __iter__(self):
        yield self.scene
        yield self.dt

    def play(self):
        self.scene.play(frame_duration=self.dt)
