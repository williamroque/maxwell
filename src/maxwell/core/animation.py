from dataclasses import dataclass

from numpy.typing import ArrayLike
import numpy as np

from maxwell.core.util import partial


@dataclass
class AnimationConfig:
    duration: float = 2.0
    fps: int = 100
    easing_function: tuple = tuple()
    shapes: ArrayLike = None


def create_easing_function(step_num, func=np.sin, start=0, end=np.pi):
    x_values = np.linspace(start, end, step_num)
    y_values = np.abs(func(x_values))

    return y_values / y_values.sum()


def animate(apply_function):
    "Decorator for quickly creating new animation types. Not for use in library."

    from maxwell.core.scene import Scene

    def wrapper(shape, *args, animation_config: AnimationConfig = None):
        if animation_config is None:
            animation_config = AnimationConfig()

        frame_num = int(animation_config.duration * animation_config.fps)

        easing_function = create_easing_function(frame_num, *animation_config.easing_function)

        properties = {
            'easing_function': easing_function,
            'shape_name': shape.shape_name
        }

        scene = Scene(properties=properties)

        scene.add_shape(shape)

        if animation_config.shapes is not None:
            scene.add_background(animation_config.shapes)

        scene.repeat_frame(
            frame_num,
            partial(apply_function, shape, *args)
        )

        return scene

    return wrapper
