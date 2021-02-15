import os
import json

import inspect


def clear(client, background=True):
    message = {
        'command': 'clear',
        'args': {
            'background': background
        }
    }

    client.send_message(message)

def run_server():
    os.system('/Users/jetblack/mframe/GUI/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron /Users/jetblack/mframe/GUI/ &')

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

def set_light_mode(client):
    message = {'command': 'setLightMode'}

    client.send_message(message)

def set_dark_mode(client):
    message = {'command': 'setDarkMode'}

    client.send_message(message)

def resize_window(client, width, height):
    message = {
        'command': 'resizeWindow',
        'args': {
            'width': width,
            'height': height
        }
    }

    client.send_message(message)

def partial(func, *partial_args, **partial_kwargs):
    partial_func = lambda *args, **kwargs: func(*partial_args, *args, **partial_kwargs, **kwargs)
    partial_func.__doc__ = func.__doc__

    if inspect.isclass(func):
        partial_func.__doc__ = func.__init__.__doc__

    return partial_func
