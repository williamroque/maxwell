from time import sleep


class Scene():
    def __init__(self, name):
        self.name = name

        self.frames = []
        self.current_frame = -1

        self.shapes = {}

    def next_frame(self, timeout=0):
        self.current_frame += 1
        sleep(timeout)

    def add_frame(self, frame):
        self.current_frame = 0

        frame.set_scene(self)
        self.frames.append(frame)

    def add_shape(self, shape, shape_id):
        self.shapes[shape_id] = shape

    def render(self):
        if self.current_frame > -1:
            self.frames[self.current_frame].apply_frame()
            for shape in self.shapes.values():
                shape.render()
