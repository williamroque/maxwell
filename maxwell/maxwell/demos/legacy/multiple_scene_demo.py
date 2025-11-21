from maxwell.int import *

clear()

axis_group = ps_axis_group(5).render()

basis_group = Group()
i_hat = create_vector([1, 0], color=COLORS.GREEN).render()
j_hat = create_vector([0, 1], color=COLORS.RED).render()

basis_group.add_shape(i_hat, 'i-hat')
basis_group.add_shape(j_hat, 'j-hat')

i_hat.move_end([2, 0], shapes=j_hat).play()
j_hat.move_end([0, 1.5], shapes=[axis_group, i_hat], initial_clear=True).play()

sleep(.3)

vec = create_vector([1, 0]).render()
vec.move_end([2, 0], shapes=basis_group).play()
vec.move_end([2, 1.5], shapes=basis_group).play()

i_scene, dt = i_hat.rotate_about(np.array([0, 0]), np.pi / 6, shapes=axis_group)
j_scene, _ = j_hat.rotate_about(np.array([0, 0]), np.pi / 6)
v_scene, _ = vec.rotate_about(np.array([0, 0]), np.pi / 6)

i_scene.merge_with(j_scene)
i_scene.merge_with(v_scene)

sleep(.5)
i_scene.play(frame_duration=dt, initial_clear=True)

client.close()
