from maxwell import *


clear()

sequence = Sequence()

curve_config = CurveConfig(color=BLUE, width=2)

original_curve, target_curve = Curve.from_functions(
    [lambda x: x**2, np.sin],
    -5, 5, 400,
    curve_config=curve_config
)

original_curve.render()

scene = original_curve.transform(target_curve)
sequence.add_scene(scene)

message = sequence.compile()
message.send()
