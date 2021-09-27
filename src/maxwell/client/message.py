class Message:
    def __init__(self, client, command, encoder=None, args=None, **kwargs):
        if args is not None:
            kwargs |= args

        self.client = client
        self.message_data = { 'command': command, 'args': kwargs }
        self.encoder = encoder

    def send(self):
        self.client.send_message(self.message_data, encoder=self.encoder)
