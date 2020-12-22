class Rect():
    def __init__(self, client, x, y, cx, cy, fill_color="#fff", border_color="#fff"):
        self.client = client

        self.x = x
        self.y = y
        self.cx = cx
        self.cy = cy

        self.fill_color = fill_color
        self.border_color = border_color

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                'type': 'rect',
                'x': self.x,
                'y': self.y,
                'cx': self.cx,
                'cy': self.cy,
                'fillColor': self.fill_color,
                'borderColor': self.border_color,
            }
        }

        self.client.send_message(message)
