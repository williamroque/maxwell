from maxwell import *

resize_window(930, 670)
clear()

polar_system.set_origin()

Shape.set_default('system', polar_system)

grid = polar_system.get_grid(PolarGridConfig(show_angles=True))
grid.render()

rose = polar_system.plot(lambda theta: 2*np.cos(2/7*theta), 0, 14*np.pi, 500)
spiral = polar_system.plot(lambda theta: 2*np.cos(7/8*theta), 0, 16*np.pi, 500, render=False)

await_space()

sequence = Sequence(background=grid)
sequence.add_scene(rose.transform(spiral))
sequence.run()
