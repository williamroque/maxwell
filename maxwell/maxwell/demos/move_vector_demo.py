from maxwell import *


clear()

sequence = Sequence()

curve_config = CurveConfig(color=GREEN)
animation_config = AnimationConfig(duration=1)

vector = Vector((3, 2), curve_config=curve_config).render()

scene = vector.move_end((1, 2), animation_config=animation_config)
sequence.add_scene(scene)

sequence.run()
