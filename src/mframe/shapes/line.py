import numpy as np


class LineSet():
    def __init__(self, client, points, color='#fff', width=3):
        self.client = client

        self.properties = {
            'type': 'lineset',
            'points': points,
            'color': color,
            'width': width
        }

    @staticmethod
    def rotate(origin, point, theta, degrees=False):
        if degrees:
            theta = theta * np.pi / 180

        theta = LineSet.get_angle(origin, point) + theta

        dx = point[0] - origin[0]
        dy = point[1] - origin[1]

        r = np.sqrt(dx ** 2 + dy ** 2)
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        point[0] = x + origin[0]
        point[1] = -y + origin[1]

        return point

    def translate_all(self, dx=0, dy=0):
        for point in self.properties['points']:
            point[0] += dx
            point[1] += dy

    @staticmethod
    def collide(line, point, threshold=0):
        if point[0] == line[0][0] and point[1] == line[0][1] or\
           point[0] == line[1][0] and point[1] == line[1][1]:
            return True

        line_angle = LineSet.get_angle(*line)
        line_point_angle = LineSet.get_angle(line[0], point)

        line_r = np.sqrt((line[1][0] - line[0][0]) ** 2 + (line[1][1] - line[0][0]) ** 2)
        line_point_r = np.sqrt((line[0][0] - point[0]) ** 2 + (line[0][1] - point[1]) ** 2)

        return round(line_point_r * np.sin(np.abs(line_angle - line_point_angle)), 5) <= threshold and line_point_r <= line_r

    @staticmethod
    def get_angle(p_1, p_2):
        dx = p_2[0] - p_1[0]
        dy = p_2[1] - p_1[1]
        r = np.sqrt(dx**2 + dy**2)

        angle = np.arcsin(dy/r)

        if p_2[0] < p_1[0]:
            angle = np.pi - angle

        return angle

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)
