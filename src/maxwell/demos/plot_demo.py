from maxwell import *

clear()


Latex.set_default('shape_config', ShapeConfig(system=canvas_system))
Latex(r'y = \sin x', (100, 50)).render()

system.get_grid(TRIG_CONFIG).render()

Curve.from_function(np.sin, -5, 5, 300).render()
