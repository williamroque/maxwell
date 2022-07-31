from maxwell import *
clear()

R_x = lambda x: np.array([
    [1, 0, 0, 0],
    [0, cos(x), -sin(x), 0],
    [0, sin(x), cos(x), 0],
    [0, 0, 0, 1]
])

R_y = lambda x: np.array([
    [cos(x), 0, sin(x), 0],
    [0, 1, 0, 0],
    [-sin(x), 0, cos(x), 0],
    [0, 0, 0, 1]
])

R_z = lambda x: np.array([
    [cos(x), -sin(x), 0, 0],
    [sin(x), cos(x), 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

M = R_x(0) @ R_y(0) @ R_z(0) @ np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1]
])

C =  R_y(0) @ R_z(-0.2) @ R_x(-.8) @ np.array([
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 6],
    [0, 0, 0, 1]
])

V = np.linalg.inv(C)

near = .5
far = 100

top = .5
right = .5

x = 800
y = 800

width = 800
height = 800

P = np.array([
    [near/right, 0, 0, 0],
    [0, near/top, 0, 0],
    [0, 0, -(far + near)/(far - near), -2*far*near/(far - near)],
    [0, 0, -1, 0]
])

projected_mesh = []


def project(point):
    v_clip = P @ V @ M @ point

    if any(v_clip > abs(v_clip[-1])) or any(v_clip < -abs(v_clip[-1])):
        return

    ndc = v_clip[:3]/v_clip[-1]

    return (
        width*ndc[0]/2 + x + width/2,
        height*ndc[1]/2 + y + height/2,
        (far - near)/2 * ndc[2] + (far + near)/2
    )

f = lambda x, y: sin(x)*cos(y)

a = -3
b = 3
c = -3
d = 3

curves = Group()

for y in np.linspace(a, b, 30):
    row_mesh = []

    for x in np.linspace(c, d, 30):
        point = project(np.array([x, y, f(x, y), 1]))

        if point is not None:
            row_mesh.append(point[:2])

    curves.add_shape(Curve(system.from_normalized(row_mesh)), f'y-{x}-{y}')


for x in np.linspace(c, d, 30):
    row_mesh = []

    for y in np.linspace(a, b, 30):
        point = project(np.array([x, y, f(x, y), 1]))

        if point is not None:
            row_mesh.append(point[:2])

    curves.add_shape(Curve(system.from_normalized(row_mesh)), f'x-{x}-{y}')


surface_1 = curves

curves = Group()

f = lambda x, y: sin(y)*cos(x)

for y in np.linspace(a, b, 30):
    row_mesh = []

    for x in np.linspace(c, d, 30):
        point = project(np.array([x, y, f(x, y), 1]))

        if point is not None:
            row_mesh.append(point[:2])

    curves.add_shape(Curve(system.from_normalized(row_mesh)), f'y-{x}-{y}')


for x in np.linspace(c, d, 30):
    row_mesh = []

    for y in np.linspace(a, b, 30):
        point = project(np.array([x, y, f(x, y), 1]))

        if point is not None:
            row_mesh.append(point[:2])

    curves.add_shape(Curve(system.from_normalized(row_mesh)), f'x-{x}-{y}')


surface_2 = curves

surface_1.transform(surface_2).play()
