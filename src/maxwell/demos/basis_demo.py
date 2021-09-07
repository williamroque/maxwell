from maxwell.int import *

clear()

system.scale = np.array([60, 60])

axes = create_axes(color='#333').render()
grid = create_grid(5, 1).render()

equation = Latex(r'$$\begin{bmatrix}1 \\ 2\end{bmatrix} = \hat\i + 2\hat\j$$', 40, 30, 30).render()

i_hat = LineSet(np.array([[0, 0], [1, 0]]), arrows=1, color=COLORS.RED).render()
j_hat = LineSet(np.array([[0, 0], [0, 1]]), arrows=1, color=COLORS.GREEN).render()

i_label = Latex(r'$$\hat\i$$', x = 0.3875, y = -0.2125, system = system).render()
j_label = Latex(r'$$\hat\j$$', x = -0.3375, y = 0.5375, system = system).render()

vec = LineSet(np.array([[0, 0], [1, 2]]), color=COLORS.BLUE, arrows = 1).render()
vec_label = Latex(r'$$\begin{bmatrix}1 \\ 2\end{bmatrix}$$', 30, 0.98333, 1.25, system = system).render()
