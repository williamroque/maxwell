import os
import json

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
