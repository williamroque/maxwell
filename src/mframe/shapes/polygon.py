from mframe.shapes.line import LineSet


class Polygon():
    def __init__(self, client, origin, n_sides, triangle_side_length, color='#fff', width=3):
        self.client = client

        self.origin = origin
        self.triangle_side_length = triangle_side_length

        self.color = color
        self.width = width

        self.points = []

        self.change_side_number(n_sides)

        self.lineset = LineSet(self.client, self.points, self.color, self.width)

    def change_side_number(self, n):
        self.n_sides = n
        self.side_length = self.triangle_side_length * 3 / self.n_sides

        del self.points[:]

        self.construct_points()

    def construct_points(self):
        self.points.append(self.origin)

        d_theta = 180 * (self.n_sides - 2) / self.n_sides
        theta = 0

        point = self.origin

        for _ in range(self.n_sides):
            new_point = [point[0] + self.side_length, point[1]]
            LineSet.rotate(point, new_point, theta, True)

            self.points.append(new_point)

            theta += 180 - d_theta
            point = new_point

    def render(self):
        self.lineset.render()
