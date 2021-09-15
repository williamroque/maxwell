from maxwell import *


clear()

system.scale /= 2


## Get shape points
def get_section(m, b, x_end, offset):
    points = []

    points.append((0, b))
    points.append((x_end, m*x_end + b))
    points.append((x_end, 0))
    points.append((0, 0))

    points = np.array(points)
    points += np.array(offset)

    return points


SLOPE = 1/4
HEIGHT = 2
WIDTH = 4

RATIO = 2

OFFSET = (-WIDTH, -1/2)


original_curve = get_section(SLOPE, HEIGHT, WIDTH, OFFSET)
target_curve = get_section(SLOPE, HEIGHT, WIDTH * RATIO, OFFSET)


## Set background
background_curve = Curve(original_curve, color=GREEN)
background_top_measure, background_top_label = measure(*original_curve[:2], 1/2, 1/3, use_label=True)
background_bottom_measure, background_bottom_label = measure(*original_curve[-2:], 1/2, 1/3, use_label=True)
background_group = Group((
    background_curve,
    background_top_measure,
    background_top_label,
    background_bottom_measure,
    background_bottom_label
)).render()


## Show measures
original_top_measure, top_label = measure(*original_curve[:2], 1/2, 1/3, use_label=True, color='#7AA1C055')
original_bottom_measure, bottom_label = measure(*original_curve[-2:], 1/2, 1/3, use_label=True, color='#7AA1C055')

target_top_measure, _ = measure(*target_curve[:2], 1/2, 1/3)
target_bottom_measure, _ = measure(*target_curve[-2:], 1/2, 1/3)


## Show shape
curve = Curve(original_curve, color='#A6B86055').render()


## Animate
sequence = Sequence(background=background_group)

sequence.show(top_label)
sequence.show(bottom_label)

section_scene = curve.transform(target_curve, duration=.8)
sequence.add_scene(section_scene)

top_measure_scene = original_top_measure.transform(target_top_measure, duration=.8)
section_scene.link_scene(top_measure_scene)

bottom_measure_scene = original_bottom_measure.transform(target_bottom_measure, duration=.8)
section_scene.link_scene(bottom_measure_scene)

sequence.run()
