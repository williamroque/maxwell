from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.core.properties import Properties


class SVG(Shape):
    "Class for SVG images."

    def __init__(self, path, transform, point=None, fill_color='#FDF4C1', shape_config: ShapeConfig = None):
        "Class for SVG images."

        super().__init__(shape_config)

        if point is None:
            point = [0, 0]

        self.properties = Properties(
            type = 'svg',
            data = path,
            point = point,
            transform = transform,
            fillColor = fill_color
        )
        self.properties.set_normalized('point')

        if self.auto_render:
            self.render()
