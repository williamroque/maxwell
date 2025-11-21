from maxwell import *


clear()

system.set_scale(1/2, True)


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
curve_config = CurveConfig(color=GREEN)
background_curve = Curve(original_curve, curve_config)

background_top_measure = Measure(
    *original_curve[:2],
    MeasureConfig(use_label=True, custom_label=lambda _: 'x', italic=True)
)
background_bottom_measure = Measure(
    *original_curve[-2:],
    MeasureConfig(use_label=True)
)

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
measure_config = MeasureConfig(use_label=True, color='#7AA1C055')

original_top_measure = Measure(*original_curve[:2], measure_config)
original_bottom_measure = Measure(*original_curve[-2:], measure_config)

sequence.show(original_top_measure)
sequence.show(original_bottom_measure)

target_top_measure = Measure(*target_curve[:2])
target_bottom_measure = Measure(*target_curve[-2:])


## Show shape
curve = Curve(original_curve, CurveConfig(color='#A6B86055')).render()
sequence.show(curve)


## Await
await_space()


## Animate
### Show labels
sequence.show(original_top_measure.label)
sequence.show(original_bottom_measure.label)

### Extend/contract section
Shape.set_default('animation_config', AnimationConfig(duration=.8))

section_scene = curve.transform(target_curve)
top_measure_scene = original_top_measure.transform(target_top_measure)
bottom_measure_scene = original_bottom_measure.transform(target_bottom_measure)

sequence.add_scenes(
    section_scene,
    top_measure_scene,
    bottom_measure_scene
)


sequence.wait(.5)


### Show ratio equations
equation_config = TextConfig(x=100, color=BLUE, markdown=True)
Text.set_default('shape_config', ShapeConfig(system=canvas_system))
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

bottom_ratio_text = Text(
    bottom_equation,
    replace(equation_config, y = 50)
)
bottom_ratio_text.set_opacity(0)

top_ratio_text = Text(
    top_equation,
    replace(equation_config, y = 80)
)
top_ratio_text.set_opacity(0)

Shape.set_default('animation_config', AnimationConfig(duration=.2))
bottom_ratio_scene = bottom_ratio_text.show()
top_ratio_scene = top_ratio_text.show()

sequence.add_scenes(bottom_ratio_scene, top_ratio_scene)


sequence.wait(3)


### Hide ratio equations
bottom_ratio_scene = bottom_ratio_text.hide()
top_ratio_scene = top_ratio_text.hide()

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
    equation_line = Text(
        line,
        replace(equation_config, x = 130, y = 50 + i*30)
    )
    equation_line.set_opacity(0)

    line_scene = equation_line.show()
    line_scenes.append(line_scene)

    equation_lines.append(equation_line)

sequence.add_scenes(*line_scenes)

#### Hide lines
sequence.wait(5)

line_scenes = []
for equation_line in equation_lines:
    line_scene = equation_line.hide()
    line_scenes.append(line_scene)

sequence.add_scenes(*line_scenes)

#### Show result
result_text = Text(
    '_x_ = {}'.format(
        round(top_equation_parameters[0] *
              bottom_equation_parameters[1] /
              bottom_equation_parameters[0], 2)
    ),
    replace(equation_config, y = 50)
)
result_text.set_opacity(0)

result_scene = result_text.show()
sequence.add_scene(result_scene)


sequence.run()
