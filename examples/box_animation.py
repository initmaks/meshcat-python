from __future__ import absolute_import, division, print_function

import math
import meshcat
import meshcat.geometry as g # Use alias for brevity
import meshcat.transformations as tf # Use alias for brevity
from meshcat.animation import Animation

vis = meshcat.Visualizer().open()

# Original rotating box
box = g.Box([0.5, 0.5, 0.5])
vis["rotating_box"].set_object(box)

# Add a sphere (visual only)
sphere = g.Sphere(0.3)
vis["props/sphere_visual"].set_object(sphere, g.MeshPhongMaterial(color=0xff8844))
vis["props/sphere_visual"].set_transform(tf.translation_matrix([0, 1.5, 0.3]))

# Add a cylinder (collision geometry)
cylinder = g.Cylinder(height=0.8, radius=0.15)
vis["obstacles/cylinder_collision"].set_object(cylinder, g.MeshPhongMaterial(color=0x4488ff))
vis["obstacles/cylinder_collision"].set_transform(tf.translation_matrix([0, -1.5, 0.4]))

# Add a ground plane (collision geometry)
ground_box = g.Box([3, 3, 0.1]) # Thin box as ground
vis["environment/ground_plane_collision"].set_object(ground_box, g.MeshPhongMaterial(color=0x888888))
vis["environment/ground_plane_collision"].set_transform(tf.translation_matrix([0, 0, -0.05]))


vis["/Background"].set_property("top_color", [0.8, 0.8, 1]) # Lighter blue
vis["/Background"].set_property("bottom_color", [0.1, 0.1, 0.2])

# Create animation for the rotating box
anim = Animation()

# Create 200 frames of rotation animation
for i in range(200):
    theta = (i + 1) / 100 * 2 * math.pi
    with anim.at_frame(vis["rotating_box"], i) as frame: # Apply anim to rotating_box path
        frame.set_transform(tf.rotation_matrix(theta, [0, 0, 1]))

# Play the animation
vis.set_animation(anim, repetitions=0)

input("Press Enter to continue...")
