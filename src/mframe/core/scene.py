from time import sleep
import os

from mframe.core.util import clear, download_canvas


class Scene():
    def __init__(self, properties={}):
        self.frames = []
        self.current_frame = -1

        self.properties = properties

        self.shapes = {}

    def add_frame(self, frame):
        self.current_frame = 0

        frame.set_scene(self)
        self.frames.append(frame)

    def next_frame(self, timeout=0):
        self.current_frame += 1
        sleep(timeout)

    def play(self, client, clear_opacity=1, frame_duration=.05, from_start=True, save_path=None, framerate=40, fps=40):
        if from_start:
            self.current_frame = 0

        for i in range(len(self.frames)):
            clear(client, clear_opacity)
            self.render()

            if save_path != None:
                download_canvas(
                    client,
                    save_path + '/image_{0:0>10}.png'.format(i)
                )

            self.next_frame(frame_duration)

        if save_path != None:
            os.system(
                'ffmpeg -y -r {framerate} -i {save_path}/image_%010d.png -c:v libx264 -vf fps={fps} -pix_fmt yuv420p {save_path}/out.mp4'.format(
                    framerate=framerate,
                    save_path=save_path,
                    fps=fps,
                )
            )

    def add_shape(self, shape, shape_id):
        self.shapes[shape_id] = shape

    def render(self):
        if self.current_frame > -1:
            self.frames[self.current_frame].apply_frame(self.properties)
            for shape in self.shapes.values():
                shape.render()
