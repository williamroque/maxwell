from dataclasses import dataclass

from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.core.properties import Properties


@dataclass
class RectConfig:
    width: float = 1/2
    height: float = 1/2
    fill_color: str = '#FFF'
    border_color: str = '#FFF'


class Rect(Shape):
    DEFAULT_RECT_CONFIG = RectConfig()

    def __init__(self, point=None, rect_config: RectConfig = None, shape_config: ShapeConfig = None):
        super().__init__(shape_config)

        if point is None:
            point = [0, 0]

        if rect_config is None:
            rect_config = self.get_default('rect_config')

        self.properties = Properties(
            type = 'rect',
            point = point,
            width = rect_config.width,
            height = rect_config.height,
            fillColor = rect_config.fill_color,
            borderColor = rect_config.border_color,
        )
        self.properties.set_normalized('point', 'width', 'height')

        if self.auto_render:
            self.render()
