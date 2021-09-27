import os

from itertools import zip_longest

import numpy as np

from maxwell.core.util import clear, await_completion
from maxwell.core.properties import Properties
from maxwell.core.group import Group
from maxwell.core.frame import Frame
from maxwell.core.sequence import Sequence
from maxwell.client.message import Message


class Scene():
    def __init__(self, client, properties={}, camera=None):
        self.frames = []
        self.current_frame = -1

        self.properties = Properties(i = 0, **properties)
        self.camera = camera

        self.linked_scenes = []

        self.shapes = {}
        self.background = {}

        self.client = client


    def add_frame(self, frame):
        self.current_frame = 0

        frame.set_scene(self)
        self.frames.append(frame)


    def repeat_frame(self, frame_num, apply_callback=None, setup_callback=None):
        for _ in range(frame_num):
            self.add_frame(Frame(apply_callback, setup_callback))


    def extend(self, n):
        self.repeat_frame(n)


    def add_shape(self, shape, send_to_background=False):
        if send_to_background:
            self.background[shape.shape_name] = shape
        else:
            self.shapes[shape.shape_name] = shape


    def add_group(self, group, send_to_background=False):
        for shape_id, shape in group.shapes.items():
            if send_to_background:
                self.background[shape_id] = shape
            else:
                self.shapes[shape_id] = shape


    def add_background(self, shapes, exclude_instance=None):
        if not isinstance(shapes, (list, np.ndarray)):
            shapes = [shapes]

        for i, obj in enumerate(shapes):
            if isinstance(obj, Group):
                for j, shape in enumerate(obj.shapes.values()):
                    if exclude_instance is None or shape != exclude_instance:
                        self.add_shape(shape, True)
            else:
                if exclude_instance is None or obj != exclude_instance:
                    self.add_shape(obj, True)


    def link_scene(self, other_scene):
        self.shapes |= other_scene.shapes

        other_scene.linked_scenes = []
        self.linked_scenes.append(other_scene)


    def render_frames(self):
        rendered_frames = []

        linked_frames = (linked_scene.frames for linked_scene in self.linked_scenes)

        for frames in zip_longest(self.frames, *linked_frames):
            shape_set = set()

            for frame in frames:
                if frame is not None:
                    frame.apply_frame()
                    shape_set |= set(frame.scene.shapes.values())

            frame_set = []

            if self.camera is not None:
                self.camera.run_hooks(self)

            for shape in shape_set:
                shape_props = shape.get_props()

                if self.camera is not None:
                    shape_props = self.camera.apply(shape, shape_props)

                frame_set.append(shape_props)

            rendered_frames.append(frame_set)

        return rendered_frames


    def play(self):
        Sequence(self.client, [self]).run()
