import numpy as np


class Arc():
    def __init__(self, client, x, y, radius, theta_1=0, theta_2=2*np.pi, fill_color="#fff", border_color="#fff"):
        """
        A class for arcs.

        Arguments:
        * client       -- Target client.
        * x            -- The x-coordinate.
        * y            -- The y-coordinate.
        * radius       -- The radius of the arc.
        * theta_1      -- The starting angle.
        * theta_2      -- The ending angle.
        * fill_color   -- The fill color for the arc.
        * border_color -- The border color.
        """

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
