"""
Demo of InstancedMesh for rendering thousands of objects efficiently.

This demonstrates how to use InstancedMesh to render many copies of the same
geometry with different transformations using a single draw call, which is
much more efficient than creating separate mesh objects.

Use cases:
- Visualizing thousands of robot trajectories simultaneously
- Particle systems
- Crowds/swarms
- Any scenario where you need many copies of the same mesh
"""

import numpy as np
import time
import meshcat
import meshcat.geometry as g
import meshcat.transformations as tf


def create_translation_matrix(x, y, z):
    """Create a 4x4 translation matrix."""
    mat = np.eye(4)  # Use float64 for compatibility with set_transform
    mat[0, 3] = x
    mat[1, 3] = y
    mat[2, 3] = z
    return mat


def create_transform_matrix(translation, rotation_axis, rotation_angle, scale=1.0):
    """Create a full transformation matrix with translation, rotation, and scale."""
    mat = tf.rotation_matrix(rotation_angle, rotation_axis)
    mat[:3, 3] = translation
    mat[:3, :3] *= scale
    return mat.astype(np.float32)


def demo_basic_grid():
    """Create a basic grid of cubes using InstancedMesh."""
    print("=" * 60)
    print("Demo 1: Basic Grid of Cubes")
    print("=" * 60)

    vis = meshcat.Visualizer()
    vis.open()
    time.sleep(1)  # Wait for browser to open

    # Create a grid of cubes
    grid_size = 20  # 20x20x5 = 2000 cubes
    depth = 5
    count = grid_size * grid_size * depth
    spacing = 0.15
    cube_size = 0.08

    print(f"Creating {count} cube instances...")

    # Create InstancedMesh
    geometry = g.Box([cube_size, cube_size, cube_size])
    material = g.MeshPhongMaterial(color=0x2194ce)
    instanced = g.InstancedMesh(geometry, material, count=count)

    # Set positions for each instance in a 3D grid
    idx = 0
    for i in range(grid_size):
        for j in range(grid_size):
            for k in range(depth):
                x = (i - grid_size / 2) * spacing
                y = (j - grid_size / 2) * spacing
                z = k * spacing
                instanced.set_matrix_at(idx, create_translation_matrix(x, y, z))
                idx += 1

    # Add to visualizer
    vis["cubes"].set_object(instanced)

    print(f"Created {count} cubes with a single InstancedMesh!")
    print("Press Ctrl+C to continue to the next demo...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    vis.delete()
    return vis


def demo_animated_instances(vis=None):
    """Animate instance transforms efficiently."""
    print("\n" + "=" * 60)
    print("Demo 2: Animated Instances")
    print("=" * 60)

    if vis is None:
        vis = meshcat.Visualizer()
        vis.open()
        time.sleep(1)

    # Create a ring of spheres
    count = 100
    radius = 1.0
    sphere_size = 0.05

    print(f"Creating {count} animated sphere instances...")

    geometry = g.Sphere(sphere_size)
    material = g.MeshPhongMaterial(color=0xff6b6b)
    instanced = g.InstancedMesh(geometry, material, count=count)

    # Initial positions in a circle
    matrices = np.zeros((count, 4, 4), dtype=np.float32)
    for i in range(count):
        angle = 2 * np.pi * i / count
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 0
        matrices[i] = create_translation_matrix(x, y, z)

    instanced.set_matrices(matrices)
    vis["animated_spheres"].set_object(instanced)

    print("Animating... Press Ctrl+C to continue to the next demo...")

    # Animate the instances
    frame = 0
    try:
        while True:
            t = frame * 0.02

            # Update all matrices
            for i in range(count):
                angle = 2 * np.pi * i / count + t
                wave = 0.3 * np.sin(angle * 3 + t * 2)
                x = (radius + wave) * np.cos(angle)
                y = (radius + wave) * np.sin(angle)
                z = 0.2 * np.sin(angle * 5 + t * 3)
                matrices[i] = create_translation_matrix(x, y, z)

            # Efficient update - only sends matrix data, not geometry/material
            vis["animated_spheres"].set_instance_matrices(matrices)

            frame += 1
            time.sleep(0.016)  # ~60 FPS
    except KeyboardInterrupt:
        pass

    vis["animated_spheres"].delete()
    return vis


def demo_colored_instances(vis=None):
    """Demo per-instance colors."""
    print("\n" + "=" * 60)
    print("Demo 3: Per-Instance Colors")
    print("=" * 60)

    if vis is None:
        vis = meshcat.Visualizer()
        vis.open()
        time.sleep(1)

    # Create a grid of colored boxes
    grid_size = 15
    count = grid_size * grid_size
    spacing = 0.12
    box_size = 0.08

    print(f"Creating {count} colored box instances...")

    geometry = g.Box([box_size, box_size, box_size])
    material = g.MeshPhongMaterial(color=0xffffff)  # Base color (will be modulated)
    instanced = g.InstancedMesh(geometry, material, count=count)

    # Set positions and colors
    matrices = np.zeros((count, 4, 4), dtype=np.float32)
    colors = np.zeros((count, 3), dtype=np.float32)

    idx = 0
    for i in range(grid_size):
        for j in range(grid_size):
            x = (i - grid_size / 2) * spacing
            y = (j - grid_size / 2) * spacing
            z = 0
            matrices[idx] = create_translation_matrix(x, y, z)

            # Rainbow gradient colors
            colors[idx] = [
                i / grid_size,        # Red: increases with x
                j / grid_size,        # Green: increases with y
                0.5                   # Blue: constant
            ]
            idx += 1

    instanced.set_matrices(matrices)
    instanced.set_colors(colors)
    vis["colored_boxes"].set_object(instanced)

    print("Animating colors... Press Ctrl+C to continue to the next demo...")

    # Animate colors
    frame = 0
    try:
        while True:
            t = frame * 0.03

            idx = 0
            for i in range(grid_size):
                for j in range(grid_size):
                    # Animated rainbow pattern
                    colors[idx] = [
                        0.5 + 0.5 * np.sin(t + i * 0.3),
                        0.5 + 0.5 * np.sin(t + j * 0.3 + 2),
                        0.5 + 0.5 * np.sin(t + (i + j) * 0.2 + 4)
                    ]
                    idx += 1

            vis["colored_boxes"].set_instance_colors(colors)

            frame += 1
            time.sleep(0.033)  # ~30 FPS
    except KeyboardInterrupt:
        pass

    vis["colored_boxes"].delete()
    return vis


def demo_trajectories(vis=None):
    """Demo visualizing multiple robot trajectories - the main use case."""
    print("\n" + "=" * 60)
    print("Demo 4: Multiple Robot Trajectories")
    print("=" * 60)

    if vis is None:
        vis = meshcat.Visualizer()
        vis.open()
        time.sleep(1)

    # Simulate many robot trajectories
    num_trajectories = 500
    trajectory_length = 100  # frames

    print(f"Simulating {num_trajectories} robot trajectories...")

    # Create a simple "robot" representation (a box)
    geometry = g.Box([0.1, 0.05, 0.03])  # Simple robot body
    material = g.MeshPhongMaterial(color=0x44aa88, opacity=0.8, transparent=True)
    instanced = g.InstancedMesh(geometry, material, count=num_trajectories)

    # Generate random trajectories (in practice, these would come from simulation)
    # Each trajectory is a series of poses
    np.random.seed(42)
    start_positions = np.random.randn(num_trajectories, 3) * 0.5
    velocities = np.random.randn(num_trajectories, 3) * 0.01

    # Set initial positions
    matrices = np.zeros((num_trajectories, 4, 4), dtype=np.float32)
    for i in range(num_trajectories):
        matrices[i] = np.eye(4, dtype=np.float32)
        matrices[i][:3, 3] = start_positions[i]

    instanced.set_matrices(matrices)
    vis["trajectories"].set_object(instanced)

    # Also set colors based on trajectory index (for visual distinction)
    colors = np.zeros((num_trajectories, 3), dtype=np.float32)
    for i in range(num_trajectories):
        hue = i / num_trajectories
        # Simple HSV to RGB conversion for varied colors
        colors[i] = [
            0.5 + 0.5 * np.sin(hue * 6.28),
            0.5 + 0.5 * np.sin(hue * 6.28 + 2.09),
            0.5 + 0.5 * np.sin(hue * 6.28 + 4.19)
        ]
    vis["trajectories"].set_instance_colors(colors)

    print(f"Animating {num_trajectories} trajectories... Press Ctrl+C to stop.")

    # Animate trajectories
    positions = start_positions.copy()
    frame = 0
    try:
        while True:
            # Update positions (simple linear motion with slight randomness)
            positions += velocities + np.random.randn(num_trajectories, 3) * 0.002

            # Bounce off boundaries
            for dim in range(3):
                mask = np.abs(positions[:, dim]) > 1.5
                velocities[mask, dim] *= -1

            # Update matrices
            for i in range(num_trajectories):
                matrices[i][:3, 3] = positions[i]
                # Add some rotation based on velocity direction
                if np.linalg.norm(velocities[i]) > 0.001:
                    angle = np.arctan2(velocities[i, 1], velocities[i, 0])
                    c, s = np.cos(angle), np.sin(angle)
                    matrices[i][0, 0] = c
                    matrices[i][0, 1] = -s
                    matrices[i][1, 0] = s
                    matrices[i][1, 1] = c

            vis["trajectories"].set_instance_matrices(matrices)

            frame += 1
            time.sleep(0.016)  # ~60 FPS
    except KeyboardInterrupt:
        pass

    return vis


def demo_performance_comparison():
    """Compare performance of InstancedMesh vs individual objects."""
    print("\n" + "=" * 60)
    print("Demo 5: Performance Comparison")
    print("=" * 60)

    vis = meshcat.Visualizer()
    vis.open()
    time.sleep(1)

    count = 1000

    # Method 1: InstancedMesh
    print(f"\nMethod 1: Creating {count} objects with InstancedMesh...")
    start = time.time()

    geometry = g.Box([0.05, 0.05, 0.05])
    material = g.MeshPhongMaterial(color=0x2194ce)
    instanced = g.InstancedMesh(geometry, material, count=count)

    matrices = np.zeros((count, 4, 4), dtype=np.float32)
    for i in range(count):
        x = (i % 32 - 16) * 0.1
        y = ((i // 32) % 32 - 16) * 0.1
        z = (i // 1024) * 0.1
        matrices[i] = create_translation_matrix(x, y, z)

    instanced.set_matrices(matrices)
    vis["instanced"].set_object(instanced)

    instanced_time = time.time() - start
    print(f"  InstancedMesh creation time: {instanced_time:.3f} seconds")

    time.sleep(2)
    vis["instanced"].delete()

    # Method 2: Individual objects (only do 100 for comparison, it would be too slow otherwise)
    comparison_count = 100
    print(f"\nMethod 2: Creating {comparison_count} individual objects (for comparison)...")
    start = time.time()

    for i in range(comparison_count):
        x = (i % 10 - 5) * 0.1
        y = ((i // 10) - 5) * 0.1
        z = 0
        vis[f"individual/box_{i}"].set_object(g.Box([0.05, 0.05, 0.05]))
        mat = create_translation_matrix(x, y, z)
        vis[f"individual/box_{i}"].set_transform(mat)

    individual_time = time.time() - start
    print(f"  Individual objects creation time: {individual_time:.3f} seconds")
    print(f"\n  Estimated time for {count} individual objects: {individual_time * count / comparison_count:.3f} seconds")
    print(f"  InstancedMesh is approximately {(individual_time * count / comparison_count) / instanced_time:.1f}x faster!")

    print("\nPress Ctrl+C to exit...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    return vis


if __name__ == "__main__":
    print("MeshCat InstancedMesh Demo")
    print("=" * 60)
    print("""
This demo shows how to use InstancedMesh for efficient rendering of
thousands of identical objects with different transforms.

Key features demonstrated:
1. Basic grid of cubes
2. Animated instance transforms
3. Per-instance colors
4. Multiple trajectory visualization
5. Performance comparison

Press Ctrl+C to advance between demos.
""")

    input("Press Enter to start...")

    # Run demos sequentially
    vis = demo_basic_grid()
    vis = demo_animated_instances(vis)
    vis = demo_colored_instances(vis)
    vis = demo_trajectories(vis)
    demo_performance_comparison()

    print("\nAll demos complete!")
