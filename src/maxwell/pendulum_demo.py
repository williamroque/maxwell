from maxwell.int import *


clear()

resize_window(800, 800)

axis_group = Group()

X = np.linspace(-7, 7, 20)
Y = np.linspace(-7, 7, 20)
system.set_fill_scale(X, 0)

axes = create_axes(color='#3339', width=1).render()
axis_group.add_shape(axes, 'axes')

grid = create_grid(9, 1, color='#3336', width=1).render()
axis_group.add_shape(grid, 'grid')

mu = 1
g = 9.81
L = 5

f = lambda theta, theta_dot: np.array([theta_dot, -mu*theta_dot - g/L*np.sin(theta)])

field_group = Group()
for i, line in enumerate(system.render_normalized_2d_vector_field(f, X, Y, arrow_scale=.3, arrow_size=2, width=2)):
    field_group.add_shape(line.render(), f'vector-{i}')

point = system.from_normalized(await_click())
particle = Arc(*point).render()

dt = .01
def path(t, i, x, y):
    return np.array([x, y]) + f(x, y) * dt

particle.follow_path(
    path,
    dt=dt,
    n=3000,
    shapes=[field_group, axis_group]
).play(initial_clear=False)
