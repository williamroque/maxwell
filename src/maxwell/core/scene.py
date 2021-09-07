from time import sleep
import os

from copy import deepcopy

import json
import datetime

from itertools import zip_longest

import numpy as np

from maxwell.core.util import clear, await_completion
from maxwell.core.properties import PropertiesEncoder, Properties
from maxwell.core.group import Group
from maxwell.client.message import Message


class Scene():
    def __init__(self, client, properties={}):
        self.frames = []
        self.current_frame = -1

        self.properties = Properties(**properties)
        self.linked_scenes = []

        self.shapes = {}
        self.background = {}

        self.client = client

    def add_frame(self, frame):
        self.current_frame = 0

        frame.set_scene(self)
        self.frames.append(frame)

    def next_frame(self, timeout=0):
        self.current_frame += 1
        sleep(timeout)

    def extend(self, n):
        self.frames[-1:] *= n

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

    def get_shape_props(self):
        return [shape.get_props() for shape in self.shapes.values()]

    def get_background_props(self):
        return [shape.get_props() for shape in self.background.values()]

    def render_frames(self):
        rendered_frames = [self.get_shape_props()]

        linked_frames = (linked_scene.frames for linked_scene in self.linked_scenes)

        for frame_set in zip_longest(self.frames, *linked_frames):
            for frame in frame_set:
                if frame is not None:
                    frame.apply_frame(self.properties)

            rendered_frames.append(
                self.get_shape_props()
            )

        return rendered_frames

    def play(self, fps=20, save_path='none', initial_clear=True, awaits_completion=False, clears=True, wait=0):
        if initial_clear:
            clear(self.client)

        save_path = os.path.expanduser(save_path)
        if not os.path.isdir(save_path) and save_path != 'none':
            os.mkdir(save_path)

        self.extend(wait*fps)

        rendered_frames = self.render_frames()

        message = Message(
            self.client, 'renderScene',
            frames           = rendered_frames,
            background       = self.get_background_props(),
            frameDuration    = 1/fps,
            savePath         = save_path,
            framerate        = fps,
            fps              = fps,
            awaitsCompletion = awaits_completion,
            clears           = clears
        )

        message.send()

        if awaits_completion:
            await_completion(self.client)

    def render(self):
        if self.current_frame > -1:
            self.frames[self.current_frame].apply_frame(self.properties)
            for shape in self.shapes.values():
                shape.render()
