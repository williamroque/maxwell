from maxwell import *


clear()

sequence = Sequence()

vector = Vector((3, 2), color=GREEN).render()

scene = vector.move_end((1, 2), duration=1)
sequence.add_scene(scene)

sequence.run()
