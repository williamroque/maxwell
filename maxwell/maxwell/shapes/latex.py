from dataclasses import dataclass, replace

import numpy as np

import re

from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.core.properties import Properties


@dataclass
class LatexConfig:
    font_size: int = 12
    color: str = '#FDF4C1'
    break_lines: bool = True
    align: str = 'center'
    embed: bool = False


class Latex(Shape):
    "A class for Latex."

    DEFAULT_LATEX_CONFIG = LatexConfig()

    def __init__(self, source, point=None, offset=None, color=None, latex_config: LatexConfig = None, shape_config: ShapeConfig = None):
        "A class for Latex."

        super().__init__(shape_config)

        if point is None:
            point = [0, 0]

        if offset is not None:
            point = [
                point[0] + offset[0],
                point[1] + offset[1]
            ]

        if latex_config is None:
            latex_config = self.get_default('latex_config')

        if color is not None:
            latex_config = replace(latex_config, color=color)

        if latex_config.break_lines:
            source = source.replace('\n', r'\\')

        source = re.sub(r'\\\(|\\\)', '', source)

        self.properties = Properties(
            type = 'latex',
            source = source,
            point = point,
            fontSize = latex_config.font_size,
            color = latex_config.color,
            align = latex_config.align,
            embed = latex_config.embed
        )
        self.properties.set_normalized('point')

        if self.auto_render:
            self.render()
