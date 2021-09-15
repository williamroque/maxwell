import os
import json
from copy import deepcopy

import inspect

import numpy as np

from maxwell.client.message import Message


def clear(client, background=True):
    message = Message(client, 'clear', background = background)
    message.send()


def run_server():
    os.system('/Users/jetblack/maxwell/GUI/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron /Users/jetblack/maxwell/GUI/ &')


def await_event(client, event, keys=[]):
    message = {
        'command': 'awaitEvent',
        'args': {
            'dataKeys': keys,
            'type': event
        }
    }

    client.send_message(message)

    return json.loads(client.receive_message())


def await_space(client):
    while await_event(client, 'keydown', ['key'])[0] != ' ':
        pass


def await_click(client, *props):
    return await_event(client, 'click', ['clientX', 'clientY', *props])


def await_properties(client, keys):
    message = {
        'command': 'awaitProperties',
        'args': {
            'keys': keys
        }
    }

    client.send_message(message)

    return json.loads(client.receive_message())


def await_completion(client):
    while True:
        message = client.receive_message()
        message = json.loads(message)

        if message[0] == 'completed':
            break


def center_origin(client, system):
    system.set_origin(client.get_shape() / 2)


def download_canvas(client, fileName):
    message = {
        'command': 'downloadCanvas',
        'args': {
            'fileName': fileName
        }
    }

    client.send_message(message)


def toggle_background(client):
    message = {'command': 'toggleBackground'}

    client.send_message(message)


def set_background(client, background):
    message = {
        'command': 'setBackground',
        'args': {
            'background': background
        }
    }

    client.send_message(message)


def set_light_mode(client):
    message = {'command': 'setLightMode'}

    client.send_message(message)


def set_dark_mode(client):
    message = {'command': 'setDarkMode'}

    client.send_message(message)


def resize_window(client, width=600, height=500, rerender=True, system=None):
    message = {
        'command': 'resizeWindow',
        'args': {
            'width': width,
            'height': height,
            'rerender': rerender
        }
    }

    client.send_message(message)

    client.receive_message()

    if system is not None:
        system.set_origin()


def partial(func, *partial_args, **partial_kwargs):
    def partial_func(*args, **kwargs):
        kwargs = partial_kwargs | kwargs

        return func(*partial_args, *args, **kwargs)

    partial_func.__doc__ = func.__doc__

    if inspect.isclass(func):
        partial_func.__doc__ = func.__init__.__doc__

    return partial_func


def rotate(points, origin, theta, degrees=False):
    """
    Rotate a point about an arbitrary origin.

    Arguments:
    * origin -- The origin.
    * points -- The points to be rotated.
    * theta -- The angle of rotation.
    * degrees -- Whether the angle should be in degrees
    (radians by default).
    """

    if degrees:
        theta = theta * np.pi / 180

    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    return (points - origin).dot(R.T) + origin


def track_clicks(client, f, system=None):
    while not (props := await_click(client, 'altKey'))[2]:
        point = props[:2]

        if system is not None:
            point = system.from_normalized(point)

        f(point)


def create_easing_function(step_num, func=np.sin, start=0, end=np.pi):
    x_values = np.linspace(start, end, step_num)
    y_values = np.abs(func(x_values))

    return y_values / y_values.sum()


def measure_label_hook(self, measure_shape, orthonormal, label_offset):
    A = np.array(measure_shape.properties.points[2])
    B = np.array(measure_shape.properties.points[3])

    r = np.linalg.norm(B - A)

    x, y = (A + B)/2 + orthonormal*label_offset

    self.properties.text = str(round(r, 1))
    self.properties.x = x
    self.properties.y = y


def measure(client, system, A, B, offset, terminal_width, color='#7AA1C0', use_label=False, label_offset=1):
    "Create a measuring stick between points A and B."

    from maxwell.shapes.line import Curve
    from maxwell.shapes.text import Text

    A = deepcopy(A)
    B = deepcopy(B)

    R = np.array([[0, -1],
                  [1,  0]])

    orthonormal = R @ (B - A)
    orthonormal /= np.linalg.norm(orthonormal)

    offset_vector = orthonormal * offset

    A += offset_vector
    B += offset_vector

    terminal_a_start = A - orthonormal * terminal_width/2
    terminal_a_end = A + orthonormal * terminal_width/2

    terminal_b_start = B - orthonormal * terminal_width/2
    terminal_b_end = B + orthonormal * terminal_width/2

    curve = []
    curve.append(terminal_a_start)
    curve.append(terminal_a_end)
    curve.append(A)
    curve.append(B)
    curve.append(terminal_b_start)
    curve.append(terminal_b_end)

    measure_curve = Curve(client, curve, color=color, system=system)

    if use_label:
        label_position = (A + B)/2 + orthonormal*label_offset
        label = Text(client, str(np.linalg.norm(B - A)), *label_position, color=color, system=system)
        label.add_access_hook(measure_label_hook, measure_curve, orthonormal, label_offset)
    else:
        label = None

    return measure_curve, label
