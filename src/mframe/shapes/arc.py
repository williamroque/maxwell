class Arc():
    def __init__(self, client, x, y, radius, theta_1, theta_2, fill_color="#fff", border_color="#fff"):
        self.client = client

        self.x = x
        self.y = y
        self.radius = radius
        self.theta_1 = theta_1
        self.theta_2 = theta_2

        self.fill_color = fill_color
        self.border_color = border_color

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                'type': 'arc',
                'x': self.x,
                'y': self.y,
                'radius': self.radius,
                'theta_1': self.theta_1,
                'theta_2': self.theta_2,
                'fillColor': self.fill_color,
                'borderColor': self.border_color,
            }
        }

        self.client.send_message(message)
