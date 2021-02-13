import os
import json


def clear(client, opacity=1):
    message = {
        'command': 'clear',
        'args': {
            'opacity': opacity
        }
    }

    client.send_message(message)

def run_server():
    os.system('/Users/jetblack/mframe/GUI/node_modules/electron/dist/Electron.app/Contents/MacOS/Electron /Users/jetblack/mframe/GUI/ &')

def await_event(client, event, keys):
    message = {
        'command': 'awaitEvent',
        'args': {
            'dataKeys': keys,
            'type': event
        }
    }

    client.send_message(message)

    return json.loads(client.receive_message())

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
