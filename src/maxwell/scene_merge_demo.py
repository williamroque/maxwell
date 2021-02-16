from maxwell.int import *

import numpy as np


clear()

r1 = LineSet([(50, 50), (100, 100)])
r1.render()

r2 = Rect(width - 100, 50, 50, 50, fill_color='orange', border_color='orange')
r2.render()

scene_1, dt_1 = r1.move_to_point((50, height - 100), f=(lambda x: x * np.sin(x), -2*np.pi, 2*np.pi))
scene_2, dt_2 = r2.move_to_point((50, height - 100))

await_click()

scene_1.merge_with(scene_2)
scene_1.play(frame_duration=dt_1)

client.close()
