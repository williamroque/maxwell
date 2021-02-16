from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties


class Image(Shape):
    def __init__(self, client, src, x, y, width, height):
        """
        A class for images.

        Arguments:
        * client -- Target client.
        * src    -- The image file's path.
        * x      -- The x-coordinate.
        * y      -- The y-coordinate.
        * width  -- The image's display width.
        * height -- The image's display height.
        """

        self.client = client

        self.properties = Properties(
            type = 'image',
            src = src,
            x = x,
            y = y,
            width = width,
            height = height,
        )

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)

        return self
