from mframe.shapes.line import LineSet


class Polygon():
    def __init__(self, client, origin, n_sides, triangle_side_length, color='#fff', width=3):
        """
        A class for polygons.

        Arguments:
        * client               -- Target client.
        * origin               -- The starting point for the polygon.
        * n_sides              -- The number of sides of the polygon.
        * triangle_side_length -- The length of the sides if the polygon
        were a triangle.
        * color                -- The color of the lines.
        * width                -- The stroke width.
        """

        self.client = client

        self.properties = {
            'type': 'polygon',
            'origin': origin,
            'triangleSideLength': triangle_side_length,
            'color': color,
            'width': width,
            'points': []
        }

        self.change_side_number(n_sides)

        self.lineset = LineSet(self.client, self.properties['points'], self.properties['color'], self.properties['width'])

    def change_side_number(self, n):
        self.n_sides = n
        self.side_length = self.properties['triangleSideLength'] * 3 / self.n_sides

        del self.properties['points'][:]

        self.construct_points()

    def construct_points(self):
        self.properties['points'].append(self.properties['origin'])

        d_theta = 180 * (self.n_sides - 2) / self.n_sides
        theta = 0

        point = self.properties['origin']

        for _ in range(self.n_sides):
            new_point = [point[0] + self.side_length, point[1]]
            LineSet.rotate(point, new_point, theta, True)

            self.properties['points'].append(new_point)

            theta += 180 - d_theta
            point = new_point

    def render(self):
        self.lineset.render()
