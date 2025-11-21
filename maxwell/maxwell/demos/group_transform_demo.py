from maxwell import *


resize_window(700, 700)
clear()

f = lambda x, y: (sin(x), cos(y))
x = np.linspace(-3, 3, 10)
y = np.linspace(-3, 3, 10)

curve_config = CurveConfig(arrow_size=.04)
vector_group = create_vector_field(f, x, y, curve_config=curve_config)
vector_group.background = False

system.scale_to_fit(vector_group.get_points(), 100)

vector_group.render()

μ = 1
g = 9.81
L = 5
f = lambda θ, θ̇: np.array([θ̇, -μ*θ̇ - g/L*np.sin(θ)])

target_group = create_vector_field(f, x, y, curve_config=curve_config)
vector_group.transform(target_group).play()
