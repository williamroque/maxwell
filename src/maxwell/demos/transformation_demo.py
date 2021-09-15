from maxwell import *


clear()

sequence = Sequence()

original_curve, target_curve = zip_functions(
    [lambda x: x**2, np.sin],
    -5, 5, 400
)

curve = Curve(original_curve, color=BLUE, width=2)
curve.render()

scene = curve.transform(target_curve)
sequence.add_scene(scene)

message = sequence.compile()
message.send()
