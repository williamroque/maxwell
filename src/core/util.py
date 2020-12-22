import os

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
