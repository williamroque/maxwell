from maxwell.shapes.shape import Shape, ShapeConfig
from maxwell.core.properties import Properties


class Table(Shape):
    "Class for HTML tables."

    def __init__(self, table, headers, raw=False, point=None, color='#FDF4C1', shape_config: ShapeConfig = None):
        "Class for HTML tables."

        super().__init__(shape_config)

        if point is None:
            point = [0, 0]

        if not raw:
            headers = self.clean(headers)
            table = list(map(self.clean, table))

        self.properties = Properties(
            type = 'table',
            data = table,
            headers = headers,
            point = point,
            color = color
        )
        self.properties.set_normalized('point')

        if self.auto_render:
            self.render()


    def clean(self, row):
        output = []

        for col in row:
            if isinstance(col, (int, float)):
                col = str(col)
            else:
                col = r'\text{{{}}}'.format(col)
                col = col.replace('$', '\\$')

            output.append(str(col))

        return output
