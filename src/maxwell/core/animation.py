from dataclasses import dataclass

from typing import Callable
from numpy.typing import ArrayLike

import numpy as np


@dataclass
class AnimationConfig:
    duration: float = 2.0
    fps: int = 100
    easing_function: Callable = None
    shapes: ArrayLike = None


def create_easing_function(step_num, func=np.sin, start=0, end=np.pi):
    x_values = np.linspace(start, end, step_num)
    y_values = np.abs(func(x_values))

    return y_values / y_values.sum()
