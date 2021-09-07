class Message:
    def __init__(self, client, command, encoder=None, **args):
        self.client = client
        self.message_data = { 'command': command, 'args': args }
        self.encoder = encoder

    def send(self):
        self.client.send_message(self.message_data, encoder=self.encoder)
