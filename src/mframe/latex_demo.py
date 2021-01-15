from mframe.client.client import Client
from mframe.shapes.latex import Latex
from mframe.core.util import clear


text = r'$$\int^b_a f(x) \> dx = F(b) - F(a)$$'
save_path = '/Users/jetblack/Desktop/fundamental_theorem.png'

client = Client()
clear(client)

latex = Latex(client, text, save_path, 0, 0, 100, 'white')
latex.render()

