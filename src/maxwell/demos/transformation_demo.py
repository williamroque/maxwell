from maxwell import *

clear()


sequence = Sequence()

original_curve = system.plot(lambda x: x**2, -5, 5, BLUE)
target_curve = system.plot(np.sin, -5, 5, GREEN, render=False)

scene = original_curve.transform(target_curve)
sequence.add_scene(scene)

sequence.run()
