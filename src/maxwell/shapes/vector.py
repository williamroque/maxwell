import datetime

from maxwell.shapes.line import Curve, LineSetProperties


class Vector(Curve):
    "Vector shape."

    def __init__(self, client, point, origin=None, shape_name=None, color='#fff', width=3, arrow_size=6, system=None, group=None):
        "This is a Curve wrapper for vectors."

        self.client = client
        self.system = system
        self.group = group

        if origin is None:
            origin = [0, 0]

        points = [origin, list(point)]

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        self.shape_name = shape_name

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        self.properties = LineSetProperties(
            type      = 'lineset',
            points    = points,
            color     = color,
            width     = width,
            arrows    = 1,
            arrowSize = arrow_size
        )
