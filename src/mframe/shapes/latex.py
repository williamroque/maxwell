import matplotlib.pyplot as plt
import datetime


class Latex():
    def __init__(self, client, text, path=None, x=0, y=0, scale=100, color='#fff'):
        self.client = client

        if path == None:
            path = f'/tmp/{datetime.datetime.now()}.png'
            is_temporary = True
        else:
            path = path
            is_temporary = False

        width = 6.5
        height = 5

        self.properties = {
            'type': 'image',
            'src': path,
            'x': x,
            'y': y,
            'width': width * scale,
            'height': height * scale,
            'color': color,
            'text': text,
            'isTemporary': is_temporary
        }

    def render(self):
        plt.rcParams['text.usetex'] = True

        plt.text(0, 1, self.properties['text'], fontsize='14', color=self.properties['color'])

        ax = plt.gca()

        for sp in 'top right left bottom'.split():
            ax.spines[sp].set_visible(False)

        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)

        plt.savefig(self.properties['src'], transparent=True, dpi=300)

        message = {
            'command': 'draw',
            'args': {
                **self.properties
            }
        }

        self.client.send_message(message)
