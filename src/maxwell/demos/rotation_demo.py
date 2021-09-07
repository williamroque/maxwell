from maxwell.int import *

clear()

np.random.seed(101)
points = (np.random.rand(10, 2) - .5) * 5

scene = Scene()

lines = LineSet(points).render()

scene.add_shape(LineSet(points).render(), 'lineset')
    
for i, point in enumerate(points):
    scene.add_shape(Arc(*point).render(), f'point-{i}')

class RotationFrame(Frame):
    def apply_frame(self, props):
        for i, point in enumerate(self.props('lineset').points):
            point_name = f'point-{i}'

            point = rotate(point, np.array([0, 0]), .01)

            self.props(point_name).x = point[0]
            self.props(point_name).y = point[1]

            self.props('lineset').points[i] = point
        
for _ in range(2000):
    scene.add_frame(RotationFrame())

scene.play(frame_duration=.01)

client.close()
