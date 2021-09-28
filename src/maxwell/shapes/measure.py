"For point measures."

from typing import Callable

from dataclasses import dataclass

import numpy as np

from maxwell.shapes.shape import ShapeConfig
from maxwell.shapes.curve import Curve, CurveConfig
from maxwell.shapes.text import Text, TextConfig


@dataclass
class MeasureConfig:
    offset: float = 1/2
    terminal_width: float = 1/3
    color: str = '#7AA1C0'
    use_label: bool = False
    label_offset: float = 1.0
    custom_label: Callable = None
    italic: bool = False


class Measure(Curve):
    "Meaure shape."

    def __init__(self, A, B, measure_config: MeasureConfig = None, curve_config: CurveConfig = None, shape_config: ShapeConfig = None):
        "Create a measuring stick between points A and B."

        if measure_config is None:
            measure_config = MeasureConfig()

        self.offset = measure_config.offset
        self.terminal_width = measure_config.terminal_width
        self.color = measure_config.color
        self.label_offset = measure_config.label_offset
        self.custom_label = measure_config.custom_label
        self.italic = measure_config.italic

        if curve_config is None:
            curve_config = CurveConfig()

        curve_config.color = measure_config.color

        super().__init__(self.get_points(A, B), curve_config, shape_config)

        if measure_config.use_label:
            self.label = self.create_label()


    @property
    def norm(self):
        return np.linalg.norm(self.B - self.A)


    @property
    def A(self):
        return np.array(self.properties.points[2]).astype(float)


    @property
    def B(self):
        return np.array(self.properties.points[3]).astype(float)


    def get_orthonormal(self, A, B):
        R = np.array([[0, -1],
                      [1,  0]])

        orthonormal = R @ (B - A)
        orthonormal /= np.linalg.norm(orthonormal)

        return orthonormal


    def get_points(self, A, B):
        A = np.array(A).astype(float)
        B = np.array(B).astype(float)

        orthonormal = self.get_orthonormal(A, B)

        offset_vector = orthonormal * self.offset

        A += offset_vector
        B += offset_vector

        terminal_a_start = A - orthonormal * self.terminal_width/2
        terminal_a_end = A + orthonormal * self.terminal_width/2

        terminal_b_start = B - orthonormal * self.terminal_width/2
        terminal_b_end = B + orthonormal * self.terminal_width/2

        curve = []
        curve.append(terminal_a_start)
        curve.append(terminal_a_end)
        curve.append(A)
        curve.append(B)
        curve.append(terminal_b_start)
        curve.append(terminal_b_end)

        return curve


    @staticmethod
    def label_hook(label, measure_shape, orthonormal, label_offset, custom_label):
        A = np.array(measure_shape.A)
        B = np.array(measure_shape.B)

        x, y = (A + B)/2 + orthonormal*label_offset

        if custom_label is None:
            label_text = str(round(measure_shape.norm, 1))
        else:
            label_text = custom_label(measure_shape.norm)

        label.properties.text = label_text
        label.properties.x = x
        label.properties.y = y


    def create_label(self):
        orthonormal = self.get_orthonormal(self.A, self.B)

        label_x, label_y = (self.A + self.B)/2 + orthonormal*self.label_offset

        text_config = TextConfig(
            x = label_x,
            y = label_y,
            color = self.color,
            italic = self.italic
        )
        shape_config = ShapeConfig(
            client = self.client,
            system = self.system
        )

        label = Text(str(round(self.norm, 1)), text_config, shape_config)
        label.add_access_hook(
            Measure.label_hook,
            self,
            orthonormal,
            self.label_offset,
            self.custom_label
        )

        return label
