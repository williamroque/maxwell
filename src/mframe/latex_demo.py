from mframe.client.client import Client
from mframe.shapes.latex import Latex
from mframe.core.util import clear


text = r'$$\int^b_a f(x) \> dx = F(b) - F(a)$$'

client = Client()
clear(client)

latex = Latex(client, text, 50, 50, 50)
latex.render()

