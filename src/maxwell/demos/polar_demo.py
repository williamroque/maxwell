from maxwell import *
clear()

resize_window(800, 400)

polar_system.set_origin()

grid = polar_system.get_grid(PolarGridConfig(show_secondary_angles=True))

rose = polar_system.plot(lambda theta: 2*np.cos(2/7*theta), 0, 14*np.pi, None, 500)
spiral = polar_system.plot(lambda theta: 2*np.cos(7/8*theta), 0, 16*np.pi, None, 500, render=False)

await_space()

rose.transform(spiral).play(background=grid)
