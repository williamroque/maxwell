from dataclasses import dataclass, replace

import numpy as np

from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.core.properties import Properties


@dataclass
class TextConfig:
    x: int = 0
    y: int = 0
    font_size: str = '15pt'
    font_family: str = 'CMU Serif'
    italic: bool = False
    markdown: bool = False
    color: str = '#FDF4C1'
    stroked: bool = False


class Text(Shape):
    "A class for normal text."

    DEFAULT_TEXT_CONFIG = TextConfig()

    def __init__(self, text, point = None, text_config: TextConfig = None, shape_config: ShapeConfig = None):
        "A class for normal text."

        super().__init__(shape_config)

        if text_config is None:
            text_config = self.get_default('text_config')

        if point is not None:
            text_config = replace(text_config, x=point[0], y=point[1])

        font_spec = ''

        if text_config.italic:
            font_spec += 'italic '

        font_spec += str(text_config.font_size) + ' '
        font_spec += text_config.font_family

        self.properties = Properties(
            type = 'text',
            text = text,
            x = text_config.x,
            y = text_config.y,
            fontSpec = font_spec,
            color = text_config.color,
            stroked = text_config.stroked,
            markdown = text_config.markdown,
            background = False
        )
        self.properties.set_normalized(('x', 'y'))

        if self.auto_render:
            self.render()
