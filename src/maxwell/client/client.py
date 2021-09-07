import socket
import sys

import json

import numpy as np

from maxwell.core.util import await_properties


class Client():
    def __init__(self, ip='127.0.0.1', port=1337):
        self.ip = ip
        self.port = port

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.connect()

    def connect(self):
        self.socket.connect((self.ip, self.port))

    def change_server(self, ip, port):
        self.ip = ip
        self.port = port

        self.close()

        self.socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        self.connect()

    def send_message(self, mess, encoder=None):
        if encoder is None:
            encoder = json.JSONEncoder

        self.socket.sendall((json.dumps(mess, cls=encoder) + '\n').encode('utf-8'))

    def receive_message(self):
        return self.socket.recv(1024)

    def get_shape(self):
        return np.array(await_properties(self, ['width', 'height']))

    def close(self):
        self.socket.close()
