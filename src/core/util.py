import os
import json


def clear(client, weak=False):
    message = {
        'command': 'clear',
        'args': {
            'weak': weak
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
