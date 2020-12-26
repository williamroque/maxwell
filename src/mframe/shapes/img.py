class Image():
    def __init__(self, client, src, x, y, width, height):
        self.client = client

        self.src = src

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def render(self):
        message = {
            'command': 'draw',
            'args': {
                'type': 'image',
                'src': self.src,
                'x': self.x,
                'y': self.y,
                'width': self.width,
                'height': self.height,
            }
        }

        self.client.send_message(message)
