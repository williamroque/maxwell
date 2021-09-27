from dataclasses import dataclass

from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.core.properties import Properties


@dataclass
class LatexConfig:
    font_size: int = 12
    color: str = '#FFF'


class Latex(Shape):
    "A class for Latex."

    def __init__(self, source, point=None, latex_config: LatexConfig = None, shape_config: ShapeConfig = None):
        "A class for Latex."

        super().__init__(shape_config)

        if point is None:
            point = [0, 0]

        if latex_config is None:
            latex_config = LatexConfig()

        self.properties = Properties(
            type = 'latex',
            source = source,
            point = point,
            font_size = latex_config.font_size,
            color = latex_config.color
        )
        self.properties.set_normalized('point')
