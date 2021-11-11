"For groups of shapes."

import numpy as np

from maxwell.client.message import Message
from maxwell.core.util import check_type_name
from maxwell.core.animation import AnimationConfig


class Group:
    "Group of shapes."

    def __init__(self, shapes=None, background=False):
        """Group of shapes.

        Arguments:
        * shapes (ndarray<Shape>, list<Shape>, tuple<Shape>, Shape)
        * background (bool) --- whether group should be rendered in the
        background; note that this is not guaranteed to work (in a
        scene, for example)
        """

        self.shapes = {}

        if shapes is not None:
            if not isinstance(shapes, (np.ndarray, list, tuple)):
                shapes = [shapes]

            for shape in shapes:
                self.add_shape(shape)

        self.background = background


    @classmethod
    def generate(cls, shape_constructor, interval, **args):
        from maxwell.shapes.shape import ShapeConfig

        group = cls()

        for i, x_i in enumerate(np.linspace(*interval)):
            constructor_args = {
                param: callback(x_i) for param, callback in args.items()
            }

            shape = shape_constructor(
                **constructor_args,
                shape_config=ShapeConfig(shape_name=f'shape-{i}')
            )

            group.add_shape(shape)

        return group


    def add_shape(self, obj, shape_name=None):
        "Add a shape to the group."

        if isinstance(obj, (list, tuple, np.ndarray)):
            for shape in obj:
                self.shapes[shape.shape_name] = shape
        else:
            if shape_name is not None:
                obj.shape_name = shape_name

            self.shapes[obj.shape_name] = obj


    def merge_with(self, other_group):
        "Merge with other group."

        self.shapes |= other_group.shapes


    def get_points(self):
        "Extract points from shapes."

        points = []

        for shape in self.shapes.values():
            if check_type_name(shape, 'Arc'):
                points.append(shape.properties.point)
            elif check_type_name(shape, 'Vector'):
                points.append(shape.origin)

        return np.array(points)


    def transform(self, group, animation_config: AnimationConfig = None):
        "Transform all shapes from one group to another."

        intersecting_keys = self.shapes.keys() & group.shapes.keys()

        scenes = []

        for key in intersecting_keys:
            shape = self.shapes[key]
            target_shape = group.shapes[key]

            if check_type_name(shape, 'Curve') and check_type_name(target_shape, 'Curve'):
                transform_scene = shape.transform(
                    target_shape,
                    animation_config = animation_config
                )

                scenes.append(transform_scene)
            elif check_type_name(shape, 'Arc') and check_type_name(target_shape, 'Arc'):
                transform_scene = shape.move_to(target_shape)

                scenes.append(transform_scene)

        scene, *other_scenes = scenes

        for other_scene in other_scenes:
            scene.link_scene(other_scene)

        return scene


    def render(self, exclude_shape=None):
        """Render shapes in group excluding the one specified by
        `exclude_shape`.
        """

        shapes = []
        client = None

        for shape in self.shapes.values():
            if client is None:
                client = shape.client

            if exclude_shape is None or shape != exclude_shape:
                shapes.append(shape.get_props())

        if shapes:
            message = Message(
                client,
                'drawGroup',
                shapes=shapes,
                canvas='background' if self.background else 'default'
            )
            message.send()

        return self
