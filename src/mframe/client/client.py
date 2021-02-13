import socket
import sys

import json

import numpy as np

from mframe.core.util import await_properties


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

    def send_message(self, mess):
        self.socket.sendall((json.dumps(mess) + '\n').encode('utf-8'))

    def receive_message(self):
        return self.socket.recv(1024)

    def get_shape(self):
        return np.array(await_properties(self, ['width', 'height']))

    def close(self):
        self.socket.close()
