from mframe.int import *

## Setup
set_light_mode()
resize_window(800, 800)
center_origin()

clear()

## Scene
scene = Scene({'points': []})

## Grid
x = np.linspace(-5, 5, 20)
y = np.linspace(-5, 5, 20)

## Scale
system.set_fill_scale(client, max(np.abs(x).max(), np.abs(y).max()), 100)

## Vector field
f = lambda x, y: np.dstack((
    np.cos(x) * np.cos(y),
    np.sin(x) + np.sin(y)
))[0] * 10

# def E(x, y):
#    charges = [
#        [-7, (-1, 0)],
#        [7, (1, 0)]
#    ]
#    
#    Ex = 0
#    Ey = 0
#
#    for charge in charges:
#        den = np.hypot(x - charge[1][0], y - charge[1][1])**3
#
#        Ex += charge[0] * (x - charge[1][0]) / den
#        Ey += charge[0] * (y - charge[1][1]) / den
#
#    return np.array([Ex, Ey])
#
#f = np.vectorize(E, signature='(),()->(2)')

lines = system.render_normalized_2d_vector_field(
    client, f, x, y,
    arrow_scale=.2,
    width=1,
    arrow_size=3,
    cmap='cw'
)

for i, line in enumerate(lines):
    scene.add_shape(line, f'vector_{i}', True)
    line.render()

## Particles
particles = []

p_distance = 1
p_n = 5
p_base = p_distance * (p_n - 1) / 2
for i in range(p_n):
    for j in range(p_n):
        x = -p_base + j * p_distance
        y = -p_base + i * p_distance

        scene.properties.points.append([x, y])

        particle = Arc(*system.normalize(np.array([x, y])), 3, fill_color='#000', border_color='#000')

        particles.append(particle)
        scene.add_shape(particle, 'particle-{}'.format(p_n * i + j))

dt = .01

class ParticleFrame(Frame):
    def apply_frame(self, properties):
        for i, point in enumerate(properties.points):
            v = f(*point)[0]

            point[0] += v[0] * dt
            point[1] += v[1] * dt

            particle_position = system.normalize(np.array(point))

            self.scene.shapes[f'particle-{i}'].properties.x = particle_position[0]
            self.scene.shapes[f'particle-{i}'].properties.y = particle_position[1]

for particle in particles:
    particle.render()

## Animation
await_space()

for _ in range(250):
    scene.add_frame(ParticleFrame())

scene.play(frame_duration=dt)

## Closing
client.close()
