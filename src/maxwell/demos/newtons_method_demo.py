from maxwell import *


clear()

axis_group = ps_axis_group(5)
axis_group.render()

background_group = Group()
background_group.merge_with(axis_group)

sequence = Sequence(background=background_group)

f = lambda x: np.sin(x)
f_prime = lambda x: np.cos(x)

X = np.linspace(-5, 5, 100)
Y = f(X)

curve = LS(zip(X, Y), color=BLUE, width=2)
curve.render()
background_group.add_shape(curve)


x_next = 1
y_next = f(x_next)

guess_point = Arc(x_next, y_next, fill_color=GREEN).render()
tangent_line = LS(zip(X, f_prime(x_next) * (X - x_next) + y_next), color=RED, width=2).render()
sequence.show(tangent_line)


def guess(f, f_prime, sequence, x_previous):
    x_next = x_previous - f(x_previous)/f_prime(x_previous)
    y_next = f(x_next)

    sequence.wait(.5)

    follow_tangent = guess_point.move_to_point((x_next, 0))
    follow_tangent.add_shape(tangent_line)

    sequence.add_scene(follow_tangent)

    sequence.wait(.5)

    find_y = guess_point.move_to_point((x_next, y_next))
    sequence.add_scene(find_y)

    sequence.add_scene(tangent_line.rotate_about(np.array([0, 0]), np.pi/3))


guess(sequence, np.pi/3, 3)


message = sequence.compile()
message.send()
