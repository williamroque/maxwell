from maxwell.int import *

## Setup
set_light_mode()
resize_window(800, 800)
center_origin()

clear()

## Scene
scene = Scene({'points': []})

## Grid
x = np.linspace(-8, 8, 30)
y = np.linspace(-8, 8, 30)

## Scale
system.set_fill_scale(max(np.abs(x).max(), np.abs(y).max()), 100)

## Vector field
f = lambda x, y: np.dstack((
    np.cos(x) * np.cos(y),
    np.sin(x) + np.sin(y)
))[0] * 10

### Gravity
#f = lambda x, y: np.dstack((
#    -x / np.hypot(x, y) ** 2,
#    -y / np.hypot(x, y) ** 2
#))[0]

### Spiral
#f = lambda x, y: np.dstack((
#    np.cos(np.hypot(x, y)),
#    np.sin(np.hypot(x, y))
#))[0]

### Electric dipole
#def E(x, y):
#    charges = [
#        [-7, (-1, 0)],
#        [7, (1, 0)],
#        [-1, (0, 5)],
#        [1, (0, -5)]
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

### Stokes flow
#def f(x, y):
#    r = np.hypot(x, y)
#
#    sinth = y/r;
#    costh = x/r;
#    R = 1.;
#    Uinf = 1.;
#    ur = Uinf*(1.-1.5*R/r+0.5*R*R*R/(r*r*r))*costh;
#    uth = Uinf*(-1.+0.75*R/r+0.25*R*R*R/(r*r*r))*sinth;
#
#    vx = costh*ur-sinth*uth;
#    vy = sinth*ur+costh*uth;
#
#    return np.dstack((
#        vx,
#        vy
#    ))[0]

lines = system.render_normalized_2d_vector_field(
    f, x, y,
    arrow_scale=.3,
    width=1,
    arrow_size=3,
    cmap='cw',
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

        particle = Arc(x, y, 3, fill_color='#000', border_color='#000')

        particles.append(particle)
        scene.add_shape(particle, 'particle-{}'.format(p_n * i + j))

dt = .01

class ParticleFrame(Frame):
    def apply_frame(self, properties):
        for i, point in enumerate(properties.points):
            v = f(*point)[0]

            point[0] += v[0] * dt
            point[1] += v[1] * dt

            self.props(f'particle-{i}').x = point[0]
            self.props(f'particle-{i}').y = point[1]

for particle in particles:
    particle.render()

## Animation
await_space()

for _ in range(1000):
    scene.add_frame(ParticleFrame())

scene.play(frame_duration=dt)

## Closing
client.close()
