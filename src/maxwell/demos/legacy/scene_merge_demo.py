from maxwell.int import *

import numpy as np


clear()

system.unset()

r1 = Rect(50, 50, 50, 50, fill_color='orange', border_color='orange')
r1.render()

r2 = Rect(width - 100, 50, 50, 50, fill_color='transparent', border_color='white')
r2.render()

scene_1, dt_1 = r1.move_to_point((50, height - 100), f=(lambda x: x * np.sin(x), -2*np.pi, 2*np.pi), duration=3)
scene_2, dt_2 = r2.move_to_point((50, height - 100), duration=3)

await_space()

scene_1.merge_with(scene_2)
scene_1.play(frame_duration=dt_1)

client.close()
