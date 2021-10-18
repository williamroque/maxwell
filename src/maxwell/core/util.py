import os
import json
from copy import deepcopy

from fractions import Fraction

import inspect
import colorsys

import numpy as np

from maxwell.client.message import Message


def clear(client, background=True):
    message = Message(client, 'clear', background = background)
    message.send()


def clear_latex(client):
    message = Message(client, 'clearLatex')
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


def ratios_to_hex(ratios):
    return (hex(int(255 * ratio))[2:] for ratio in ratios)


def hex_to_ratios(values):
    return (int(value, 16)/255 for value in values)


def hsv_to_hex(hue, saturation, value):
    norm_rgb = colorsys.hsv_to_rgb(hue, saturation, value)

    color = '#{:0>2}{:0>2}{:0>2}'.format(
        *ratios_to_hex(norm_rgb)
    )

    return color


def hex_to_hsv(color):
    color = color[1:]

    if len(color) < 6:
        color = ''.join(sum(zip(color, color), ()))

    hex_values = (color[i*2:i*2+2] for i in range(3))

    ratios = hex_to_ratios(hex_values)

    return np.array(colorsys.rgb_to_hsv(*ratios))



def color_to_int(color, force_alpha=True):
    color = color[1:]

    if len(color) < 6:
        color = ''.join(sum(zip(color, color), ()))

    if force_alpha:
        color = color.ljust(8, 'F')

    return int(color, 16)


def int_to_color(num, force_alpha=True):
    color = hex(num)[2:]

    if force_alpha:
        color = color.zfill(8)
    else:
        color = color.zfill(len(color) + len(color)%2)

    return '#' + color


def rgb_to_hex(color):
    color = color[:4]

    hex_values = (hex(int(value))[2:] for value in color)

    return '#{:0>2}{:0>2}{:0>2}{:0>2}'.format(*hex_values)


def hex_to_rgb(color):
    color = color[1:]

    if len(color) < 6:
        color = ''.join(sum(zip(color, color), ()))

    color = color.ljust(8, 'F')

    hex_values = (color[i*2:i*2+2] for i in range(4))

    return np.array([int(value, 16) for value in hex_values])


def check_type_name(obj, types):
    if isinstance(obj, str):
        types = (types,)

    return any(candidate.__name__ in types for candidate in type(obj).__mro__)


def pi_format(x):
    if x == 0:
        return '0'

    multiple = x / np.pi
    fraction = Fraction(multiple).limit_denominator(100)
    num = fraction.numerator
    den = fraction.denominator

    if abs(num) == 1:
        num = ''

    if den == 1:
        return  '{} \\pi'.format(num)

    return '\\frac{{ {} \\pi }}{{ {} }}'.format(num, den)


def fraction_format(x):
    if x == 0:
        return '0'

    fraction = Fraction(x).limit_denominator(100)
    num = fraction.numerator
    den = fraction.denominator

    if den == 1:
        return str(num)

    return '{} \\frac{{ {} }}{{ {} }}'.format('-' if x < 0 else '', abs(num), den)


def series(a_n, n, start=0):
    return sum(a_n(i) for i in range(start, n + 1))


def taylor(a_n, n, start=0):
    return lambda x: sum(a_n(i, x) for i in range(start, n + 1))


def rationalize(x, max_den=None):
    if max_den is None:
        max_den = np.math.ceil(1/x)

    return str(Fraction(x).limit_denominator(max_den))

