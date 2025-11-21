from maxwell import *


clear()


@animate
def scale_shape(shape, factor, frame=None, props=None):
    if frame.is_first:
        props.width_change = shape.properties.width * (factor - 1)
        props.height_change = shape.properties.height * (factor - 1)

    shape.properties.width += props.easing_ratio * props.width_change
    shape.properties.height += props.easing_ratio * props.height_change


rect = Rect((0, 0), RectConfig(height = 3, width = 2))

sequence = Sequence()
sequence.add_scene(scale_shape(rect, 1/4))
sequence.add_scene(scale_shape(rect, 2))
sequence.add_scene(scale_shape(rect, 1/4))
sequence.add_scene(scale_shape(rect, 2))
sequence.add_scene(scale_shape(rect, 1/4))
sequence.add_scene(scale_shape(rect, 16))
sequence.run()
