from maxwell.int import *

## Setup
clear()

resize_window()

system.scale = np.array([60, 60])

axes = create_axes().render()
grid = create_grid(5, 1).render()

## Basis vectors
i_hat = LineSet(np.array([[0, 0], [1, 0]]), arrows=1, color=COLORS.RED).render()
i_label = Latex(r'$$\hat{\i}$$', x = 0.3875, y = -0.2125, system = system).render()

j_hat = LineSet(np.array([[0, 0], [0, 1]]), arrows=1, color=COLORS.GREEN).render()
j_label = Latex(r'$$\hat{\j}$$', x = -0.3375, y = 0.5375, system = system).render()

## Transformation matrix
matrix_text = (
r'$$\begin{bmatrix}'
r'1.5 & 0.5 \\'
r'0.5 & 2'
r'\end{bmatrix}$$'
)

matrix_latex = Latex(matrix_text, 40, 30, 30).render()

## Animation
await_space()

i_scene, i_dt = i_hat.move_point(1, [1.5, .5], shapes=[*axes, *grid, i_label, j_label, matrix_latex])
j_scene, j_dt = j_hat.move_point(1, [.5, 2])

i_scene.merge_with(j_scene).play(frame_duration=i_dt)

client.close()
