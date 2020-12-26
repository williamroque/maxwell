class LineSet():
    def __init__(self, client, points, color="#fff", width=3):
        self.client = client

        self.points = points

        self.color = color
        self.width = width

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                'type': 'lineset',
                'points': self.points,
                'color': self.color,
                'width': self.width,
            }
        }

        self.client.send_message(message)
