class Rect():
    def __init__(self, client, x, y, cx, cy, fill_color="#fff", border_color="#fff"):
        self.client = client

        self.properties = {
            'type': 'rect',
            'x': x,
            'y': y,
            'cx': cx,
            'cy': cy,
            'fillColor': fill_color,
            'borderColor': border_color,
        }

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)
