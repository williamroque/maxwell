import numpy as np

from maxwell.shapes.shape import Shape
from maxwell.core.properties import Properties
from maxwell.core.scene import Scene
from maxwell.core.frame import Frame
from maxwell.core.util import rotate, create_easing_function
from maxwell.core.group import Group

import datetime


class LineSetProperties(Properties):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self._x, self._y = self.points[0] if len(self.points) > 0 else None, None


    @property
    def x(self):
        return self._x


    @x.setter
    def x(self, value):
        self._x = value

        dx = value - self.points[0][0]
        for point in self.points:
            point[0] += dx


    @property
    def y(self):
        return self._y


    @y.setter
    def y(self, value):
        self._y = value

        dy = value - self.points[0][1]
        for point in self.points:
            point[1] += dy


class Curve(Shape):
    def __init__(self, client, points, shape_name=None, color='#fff', width=3, arrows=0, arrow_size=6, system=None, group=None):
        "A class for lines."
        

        self.client = client
        self.system = system
        self.group = group

        if shape_name is None:
            shape_name = f'{datetime.datetime.now()}-shape'

        self.shape_name = shape_name

        if isinstance(points, Group):
            point_list = []

            for shape in points.shapes.values():
                point_list.append([shape.properties.x, shape.properties.y])

            points = point_list

        if self.group is not None:
            self.group.add_shape(self, shape_name)

        self.properties = LineSetProperties(
            type = 'lineset',
            points = list(map(list, list(points))),
            color = color,
            width = width,
            arrows = arrows,
            arrowSize = arrow_size
        )
        self.properties.set_normalized('points')


    @staticmethod
    def zip_function(func, start, end, point_num):
        "Create a zipped array of points from a mathematical function."

        x_values = np.linspace(start, end, point_num)
        y_values = func(x_values)

        return zip(x_values, y_values)


    @staticmethod
    def zip_functions(funcs, *args):
        "Zip several functions at once."

        return (Curve.zip_function(func, *args) for func in funcs)


    def get_props(self):
        "Extract shape rendering properties."

        return self.properties.get_normalized(self.system)


    def set_points(self, points):
        "Change the curve's points."

        self.properties.points = list(map(list, list(points)))


    @staticmethod
    def move_point_setup(frame, props):
        "Frame setup for `move_point`."

        props.cx = props.ending_point[0] - props.point[0]
        props.cy = props.ending_point[1] - props.point[1]


    @staticmethod
    def move_point_apply(frame, props):
        "Frame callback for `move_point`."

        x_change = props.cx * props.easing_function[props.i]
        y_change = props.cy * props.easing_function[props.i]

        props.point[0] += x_change
        props.point[1] += y_change


    def move_point(self, point_i, ending_point, fps=100, easing_function=None, duration=.5, shapes=None):
        "Create a scene moving a specific point."

        frame_num = int(duration * fps)

        if easing_function is None:
            easing_function = create_easing_function(frame_num)

        scene = Scene(self.client, {
            'cx': None,
            'cy': None,
            'point': self.properties.points[point_i],
            'ending_point': ending_point,
            'easing_function': easing_function
        })

        scene.repeat_frame(
            frame_num,
            Curve.move_point_apply,
            Curve.move_point_setup
        )

        scene.add_shape(self)

        if shapes is not None:
            scene.add_background(shapes)

        return scene

    def move_end(self, point, *args, **kwargs):
        "Create a scene moving the last point."

        return self.move_point(len(self.properties.points) - 1, point, *args, **kwargs)


    def rotate_about(self, origin, theta, n=None, n_scale=1, f=None, animate=True, shapes=[]):
        "Create a scene moving the curve about a specific point."

        if not animate:
            self.properties.points = rotate(self.properties.points, origin, theta)

            return self

        scene = Scene(self.client, { 'i': 0, 'shape_name': self.shape_name })

        scene.add_shape(self)

        scene.add_background(shapes)

        if n is None:
            n = int(abs(theta) * 100 * n_scale)

        if f is None:
            f = (np.sin, 0, np.pi)

        X = np.linspace(f[1], f[2], n)
        Y = np.abs(f[0](X))
        C = Y / Y.sum()

        class MotionFrame(Frame):
            def apply_frame(self, props):
                d_theta = C[props.i] * theta

                shape_name = props.shape_name

                self.props(shape_name).properties.points = rotate(
                    self.props(shape_name).points,
                    origin,
                    d_theta
                )

                props.i += 1

        for _ in range(n):
            scene.add_frame(MotionFrame())

        return scene


    @staticmethod
    def transform_setup(frame, props):
        "Callback for transformation frames setup."

        for j, point in enumerate(props.points):
            target_x, target_y = props.target_curve[j]

            props.cx.append(target_x - point[0])
            props.cy.append(target_y - point[1])


    @staticmethod
    def transform_apply(frame, props):
        "Callback for transformation frames."

        for j, point in enumerate(props.points):
            ratio = props.easing_ratio

            x_change = props.cx[j] * ratio
            y_change = props.cy[j] * ratio

            props.points[j][0] += x_change
            props.points[j][1] += y_change


    def transform(self, target_curve, **kwargs):
        "Create a scene transforming the curve into another one."

        if isinstance(target_curve, Curve):
            target_curve = target_curve.properties.points

        target_curve = list(target_curve)

        scene_properties = {
            'cx': [],
            'cy': [],
            'points': self.properties.points,
            'target_curve': target_curve,
        }

        scene, frame_num = self.create_scene(
            scene_properties,
            **kwargs
        )

        scene.repeat_frame(
            frame_num,
            Curve.transform_apply,
            Curve.transform_setup
        )

        return scene


    def render(self):
        message = {
            'command': 'draw',
            'args': self.get_props()
        }

        self.client.send_message(message)

        return self
