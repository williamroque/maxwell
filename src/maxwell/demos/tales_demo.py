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

background_top_measure = Measure(*original_curve[:2], use_label=True, custom_label=lambda _: 'x', italic=True)
background_bottom_measure = Measure(*original_curve[-2:], use_label=True)

background_group = Group((
    background_curve,
    background_top_measure,
    background_top_measure.label,
    background_bottom_measure,
    background_bottom_measure.label
)).render()


## Set up animation
sequence = Sequence(background=background_group)


## Show measures
original_measure = partial(Measure, use_label=True, color='#7AA1C055')

original_top_measure = original_measure(*original_curve[:2])
original_bottom_measure = original_measure(*original_curve[-2:])

sequence.show(original_top_measure)
sequence.show(original_bottom_measure)

target_top_measure = Measure(*target_curve[:2])
target_bottom_measure = Measure(*target_curve[-2:])


## Show shape
curve = Curve(original_curve, color='#A6B86055').render()
sequence.show(curve)


## Await
await_space()


## Animate
sequence.show(original_top_measure.label)
sequence.show(original_bottom_measure.label)

section_scene = curve.transform(target_curve, duration=.8)
top_measure_scene = original_top_measure.transform(target_top_measure, duration=.8)
bottom_measure_scene = original_bottom_measure.transform(target_bottom_measure, duration=.8)

sequence.add_scenes(
    section_scene,
    top_measure_scene,
    bottom_measure_scene
)


sequence.wait(.5)


ratio_text = partial(Text, x=100, color=BLUE, markdown=True, system=None)
ratio_equation = partial('{} : {} = {}'.format)

bottom_equation = ratio_equation(
    round(target_bottom_measure.norm, 1),
    round(original_bottom_measure.norm, 1),
    RATIO
)

top_equation = ratio_equation(
    round(target_top_measure.norm, 1),
    '_x_',
    RATIO
)

bottom_ratio_text = ratio_text(bottom_equation, y=50)
bottom_ratio_text.set_opacity(0)

top_ratio_text = ratio_text(top_equation, y=80)
top_ratio_text.set_opacity(0)

bottom_ratio_scene = bottom_ratio_text.show(duration=.2)
top_ratio_scene = top_ratio_text.show(duration=.2)

sequence.add_scenes(bottom_ratio_scene, top_ratio_scene)


sequence.run()
