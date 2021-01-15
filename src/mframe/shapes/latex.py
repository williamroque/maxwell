import matplotlib.pyplot as plt
import datetime


class Latex():
    def __init__(self, client, text, path=None, x=0, y=0, scale=100, color='#fff'):
        self.client = client

        self.text = text
        self.x = x
        self.y = y
        self.scale = scale
        self.color = color

        if path == None:
            self.path = f'/tmp/{datetime.datetime.now()}.png'
            self.is_temporary = True
        else:
            self.path = path
            self.is_temporary = False


    def render(self):
        plt.rcParams['text.usetex'] = True

        plt.text(0, 1, self.text, fontsize='14', color=self.color)

        ax = plt.gca()

        for sp in 'top right left bottom'.split():
            ax.spines[sp].set_visible(False)

        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)

        plt.savefig(self.path, transparent=True, dpi=300)

        width = 6.5
        height = 5

        message = {
            'command': 'draw',
            'args': {
                'type': 'image',
                'src': self.path,
                'x': self.x,
                'y': self.y,
                'width': width * self.scale,
                'height': height * self.scale,
                'isTemporary': self.is_temporary
            }
        }

        self.client.send_message(message)
