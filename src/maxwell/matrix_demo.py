from maxwell.int import *

## Setup
clear()

resize_window(rerender=False)

system.scale = np.array([60, 60])

ps_axis_group(5).render()

## Basis vectors
text_group = Group(background=True)

i_hat = LineSet(np.array([[0, 0], [1, 0]]), arrows=1, color=COLORS.RED).render()
i_label = Latex(r'$$\hat{\i}$$', x = 0.3875, y = -0.2125, system = system)
text_group.add_shape(i_label, 'i-hat')

j_hat = LineSet(np.array([[0, 0], [0, 1]]), arrows=1, color=COLORS.GREEN).render()
j_label = Latex(r'$$\hat{\j}$$', x = -0.3375, y = 0.5375, system = system)
text_group.add_shape(j_label, 'j-hat')

## Transformation matrix
matrix_text = (
r'$$\begin{bmatrix}'
r'1.5 & 0.5 \\'
r'0.5 & 2'
r'\end{bmatrix}$$'
)

matrix_latex = Latex(matrix_text, 40, 30, 30)
text_group.add_shape(matrix_latex, 'matrix')

text_group.render()

## Animation
await_space()

f = [np.sin, 0, np.pi]

i_scene, i_dt = i_hat.move_point(1, [1.5, .5], f=f)
j_scene, j_dt = j_hat.move_point(1, [.5, 2], f=f)

i_scene.merge_with(j_scene).play(frame_duration=i_dt, initial_clear=False)

client.close()
