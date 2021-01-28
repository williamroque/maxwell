class Image():
    def __init__(self, client, src, x, y, width, height):
        self.client = client

        self.properties = {
            'type': 'image',
            'src': src,
            'x': x,
            'y': y,
            'width': width,
            'height': height,
        }

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)
