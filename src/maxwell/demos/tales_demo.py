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
### Show labels
sequence.show(original_top_measure.label)
sequence.show(original_bottom_measure.label)

### Extend/contract section
section_scene = curve.transform(target_curve, duration=.8)
top_measure_scene = original_top_measure.transform(target_top_measure, duration=.8)
bottom_measure_scene = original_bottom_measure.transform(target_bottom_measure, duration=.8)

sequence.add_scenes(
    section_scene,
    top_measure_scene,
    bottom_measure_scene
)


sequence.wait(.5)


### Show ratio equations
equation_text = partial(Text, x=100, color=BLUE, markdown=True, system=None)
ratio_equation = partial('{} : {} = {}'.format)

bottom_equation_parameters = [
    round(target_bottom_measure.norm, 1),
    round(original_bottom_measure.norm, 1),
    RATIO
]

top_equation_parameters = [
    round(target_top_measure.norm, 1),
    '_x_',
    RATIO
]

bottom_equation = ratio_equation(*bottom_equation_parameters)
top_equation = ratio_equation(*top_equation_parameters)

bottom_ratio_text = equation_text(bottom_equation, y=50)
bottom_ratio_text.set_opacity(0)

top_ratio_text = equation_text(top_equation, y=80)
top_ratio_text.set_opacity(0)

bottom_ratio_scene = bottom_ratio_text.show(duration=.2)
top_ratio_scene = top_ratio_text.show(duration=.2)

sequence.add_scenes(bottom_ratio_scene, top_ratio_scene)


sequence.wait(3)


### Hide ratio equations
bottom_ratio_scene = bottom_ratio_text.hide(duration=.2)
top_ratio_scene = top_ratio_text.hide(duration=.2)

sequence.add_scenes(bottom_ratio_scene, top_ratio_scene)


### Solve for x
lines = []

#### Equation lines
lines.append('{} : {} = {} : _x_'.format(
    bottom_equation_parameters[0],
    bottom_equation_parameters[1],
    top_equation_parameters[0]
))

lines.append('_x_ × {} : {} = {}'.format(
    bottom_equation_parameters[0],
    bottom_equation_parameters[1],
    top_equation_parameters[0]
))

lines.append('_x_ × {} = {} × {}'.format(
    bottom_equation_parameters[0],
    top_equation_parameters[0],
    bottom_equation_parameters[1]
))

lines.append('_x_ = {} × {} : {}'.format(
    top_equation_parameters[0],
    bottom_equation_parameters[1],
    bottom_equation_parameters[0]
))

#### Render lines
line_scenes = []
equation_lines = []
for i, line in enumerate(lines):
    equation_line = equation_text(line, x=130, y=50 + i*30)
    equation_line.set_opacity(0)

    line_scene = equation_line.show(duration=.2)
    line_scenes.append(line_scene)

    equation_lines.append(equation_line)

sequence.add_scenes(*line_scenes)

#### Hide lines
sequence.wait(5)

line_scenes = []
for equation_line in equation_lines:
    line_scene = equation_line.hide(duration=.2)
    line_scenes.append(line_scene)

sequence.add_scenes(*line_scenes)

#### Show result
result_text = equation_text('_x_ = {}'.format(
    round(top_equation_parameters[0] *
          bottom_equation_parameters[1] /
          bottom_equation_parameters[0], 2)
), y=50)
result_text.set_opacity(0)

result_scene = result_text.show(duration=.2)
sequence.add_scene(result_scene)


sequence.run()
