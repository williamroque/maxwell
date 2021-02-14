from time import sleep
import os
from json import dumps, JSONEncoder
from mframe.shapes.polygon import Polygon

from mframe.core.util import clear, download_canvas


class PropertiesEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Polygon):
            return obj.lineset.properties
        return obj.properties


class Scene():
    def __init__(self, client, properties={}):
        self.frames = []
        self.current_frame = -1

        self.properties = properties

        self.shapes = {}

        self.client = client

    def add_frame(self, frame):
        self.current_frame = 0

        frame.set_scene(self)
        self.frames.append(frame)

    def next_frame(self, timeout=0):
        self.current_frame += 1
        sleep(timeout)

    def add_shape(self, shape, shape_id):
        self.shapes[shape_id] = shape

    def play(self, frame_duration=.05, save_path='none', framerate=40, fps=40, clear_opacity=1):
        rendered_frames = [dumps(self.shapes, cls=PropertiesEncoder)]
        for frame in self.frames:
            frame.apply_frame(self.properties)
            rendered_frames.append(dumps(self.shapes, cls=PropertiesEncoder))

        message = {
            'command': 'renderScene',
            'args': {
                'frames': rendered_frames,
                'frameDuration': frame_duration,
                'savePath': save_path,
                'framerate': framerate,
                'fps': fps,
                'clearOpacity': clear_opacity
            }
        }

        self.client.send_message(message)

    def render(self):
        if self.current_frame > -1:
            self.frames[self.current_frame].apply_frame(self.properties)
            for shape in self.shapes.values():
                shape.render()
