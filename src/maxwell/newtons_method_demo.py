from maxwell import *

clear()

axis_group = ps_axis_group(5).render()

f = lambda x: x**2
f_prime = lambda x: 2*x

X = np.linspace(-5, 5, 100)
Y = f(X)

LS(zip(X, Y), color=BLUE, width=2).render()

x_n = 1
y_n = f(x_n)

guess_point = Arc(x_n, y_n, fill_color=GREEN).render()
tangent_line = LS(zip(X, f_prime(x_n) * (X - x_n) + y_n), color=RED, width=2)

global_group.background = True

def guess(n = 3):
    global x_n, y_n

    if n == 0:
        return

    clear()
    axis_group.render()
    global_group.render(guess_point)
    guess_point.render()

    x_n = x_n - f(x_n)/f_prime(x_n)
    y_n = f(x_n)

    sleep(.5)
    guess_point.move_to_point((x_n, 0), shapes=global_group).play()

    sleep(.5)
    guess_point.move_to_point((x_n, y_n), shapes=global_group).play()

    tangent_line.set_points(zip(X, f_prime(x_n) * (X - x_n) + y_n))

    guess(n - 1)

await_space()

guess()
