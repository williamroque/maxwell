from mframe.shapes.shape import Shape
from mframe.core.properties import Properties

class Rect(Shape):
    def __init__(self, client, x, y, cx, cy, fill_color="#fff", border_color="#fff"):
        """
        A class for rectangles.

        Arguments:
        * client     -- Target client.
        * x          -- The x-coordinate.
        * y          -- The y-coordinate.
        * cx         -- The width of the rectangle.
        * cy         -- The height of the rectangle.
        * fill_color -- Fill color.
        * border     -- Border color.
        """

        self.client = client

        self.properties = Properties(
            type = 'rect',
            x = x,
            y = y,
            cx = cx,
            cy = cy,
            fillColor = fill_color,
            borderColor = border_color,
        )

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)
