import numpy as np


class Arc():
    def __init__(self, client, x, y, radius, theta_1=0, theta_2=2*np.pi, fill_color="#fff", border_color="#fff"):
        self.client = client

        self.properties = {
                'type': 'arc',
                'x': x,
                'y': y,
                'radius': radius,
                'theta_1': theta_1,
                'theta_2': theta_2,
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
