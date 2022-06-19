from maxwell import *
from scipy.optimize import root


f = lambda x: 1/2*x**2
g = np.sin

guess = 1
intersection = root(lambda x: f(x) - g(x), guess).x[0]

system.get_grid(2.5, (1/2, 1/2), grid_config=FRACTION)
system.plot(f, -5, 5, GREEN, shade=(0, intersection, g))
system.plot(g, -5, 5, BLUE)
