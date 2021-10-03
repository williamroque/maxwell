from maxwell import *

resize_window(800, 800)


animation_config = AnimationConfig(duration=5)


def preview_field(f):
    x = np.linspace(-5, 5, 15)
    y = np.linspace(-5, 5, 15)

    null_vector_config = ArcConfig(radius = 5)

    vector_group = create_vector_field(
        f, x, y,
        arc_config = null_vector_config,
        cmap='cw'
    )

    system.scale_to_fit(vector_group.get_points(), 100)

    vector_group.render()

    await_space()

    sequence = Sequence(background=vector_group)

    dt = 1/animation_config.fps
    def particle_path(_, __, point):
        if point[0] > 100:
            point[0] = 100

        if point[1] > 100:
            point[1] = 100

        return point + np.array(f(*point))*dt

    particle_scenes = []

    for i in range(-3, 4):
        for j in range(-3, 4):
            particle = Arc((i, j))
            particle_scene = particle.follow_path(
                particle_path,
                animation_config = animation_config
            )
            particle_scenes.append(particle_scene)

    sequence.add_scenes(*particle_scenes)

    sequence.run(await_completion=True)
    await_completion()


## Vector fields

fields = [
    lambda x, y: (x, y),
    lambda x, y: (x * y, x * y),
    lambda x, y: (np.sin(x), np.cos(y)),
    lambda x, y: (np.cos(np.hypot(x, y)), np.sin(np.hypot(x, y)))
]

for field in fields:
    clear()
    preview_field(field)
