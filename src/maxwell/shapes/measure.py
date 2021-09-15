import datetime
from copy import deepcopy

import numpy as np

from maxwell.shapes.line import Curve, LineSetProperties
from maxwell.shapes.text import Text


class Measure(Curve):
    "Meaure shape."

    def __init__(self, client, A, B, offset=1/2, terminal_width=1/3, color='#7AA1C0', use_label=False, label_offset=1, custom_label=None, italic=False, width=3, shape_name=None, system=None, group=None):
        "Create a measuring stick between points A and B."

        self.client = client
        self.system = system
        self.group = group

        self.A = deepcopy(A)
        self.B = deepcopy(B)
        self.offset = offset
        self.terminal_width = terminal_width
        self.color = color
        self.label_offset = label_offset
        self.custom_label = custom_label
        self.italic = italic

        if use_label:
            self.label = self.create_label()

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        self.shape_name = shape_name

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        self.properties = LineSetProperties(
            type      = 'lineset',
            points    = self.get_points(),
            color     = color,
            width     = width,
            arrows    = 0,
            arrowSize = 0
        )


    @property
    def norm(self):
        return np.linalg.norm(self.B - self.A)


    def get_orthonormal(self):
        R = np.array([[0, -1],
                      [1,  0]])

        orthonormal = R @ (self.B - self.A)
        orthonormal /= np.linalg.norm(orthonormal)

        return orthonormal


    def get_points(self):
        orthonormal = self.get_orthonormal()

        offset_vector = orthonormal * self.offset

        self.A += offset_vector
        self.B += offset_vector

        terminal_a_start = self.A - orthonormal * self.terminal_width/2
        terminal_a_end = self.A + orthonormal * self.terminal_width/2

        terminal_b_start = self.B - orthonormal * self.terminal_width/2
        terminal_b_end = self.B + orthonormal * self.terminal_width/2

        curve = []
        curve.append(terminal_a_start)
        curve.append(terminal_a_end)
        curve.append(self.A)
        curve.append(self.B)
        curve.append(terminal_b_start)
        curve.append(terminal_b_end)

        return curve


    @staticmethod
    def label_hook(self, measure_shape, orthonormal, label_offset, custom_label):
        A = np.array(measure_shape.A)
        B = np.array(measure_shape.B)

        x, y = (A + B)/2 + orthonormal*label_offset

        if custom_label is None:
            label_text = str(round(measure_shape.norm, 1))
        else:
            label_text = custom_label(measure_shape.norm)

        self.properties.text = label_text
        self.properties.x = x
        self.properties.y = y


    def create_label(self):
        orthonormal = self.get_orthonormal()

        label_position = (self.A + self.B)/2 + orthonormal*self.label_offset
        label = Text(
            self.client,
            str(round(self.norm, 1)),
            *label_position,
            color=self.color,
            italic=self.italic,
            system=self.system
        )
        label.add_access_hook(
            Measure.label_hook,
            self,
            orthonormal,
            self.label_offset,
            self.custom_label
        )

        return label
