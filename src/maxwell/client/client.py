import socket
import sys

import json

import numpy as np

from maxwell.core.util import await_properties


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.astype(int).tolist()
        return json.JSONEncoder.default(self, obj)


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

    def send_message(self, mess, contains_ndarray=False):
        if contains_ndarray:
            encoder = NumpyEncoder
        else:
            encoder = json.JSONEncoder

        self.socket.sendall((json.dumps(mess, cls=encoder) + '\n').encode('utf-8'))

    def receive_message(self):
        return self.socket.recv(1024)

    def get_shape(self):
        return np.array(await_properties(self, ['width', 'height']))

    def close(self):
        self.socket.close()
