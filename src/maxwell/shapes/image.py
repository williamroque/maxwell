import os

from dataclasses import dataclass

from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.core.properties import Properties


@dataclass
class ImageConfig:
    width: float = 0
    height: float = 0
    is_temporary: bool = False


class Image(Shape):
    "Superclass for images."

    DEFAULT_IMAGE_CONFIG = None

    def __init__(self, src, point=None, image_config: ImageConfig = None, shape_config: ShapeConfig = None):
        "Superclass for images."

        super().__init__(shape_config)

        if point is None:
            point = [0, 0]

        if image_config is None:
            image_config = self.default_config('image_config', ImageConfig)

        self.properties = Properties(
            type = 'image',
            src = os.path.expanduser(src),
            point = point,
            width = image_config.width,
            height = image_config.height,
            isTemporary = image_config.is_temporary
        )
        self.properties.set_normalized('point')
