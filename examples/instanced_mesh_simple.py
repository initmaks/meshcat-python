"""
Simple test of InstancedMesh functionality.
"""

import numpy as np
import time
import meshcat
import meshcat.geometry as g


def main():
    print("Creating visualizer...")
    vis = meshcat.Visualizer()
    vis.open()

    # Wait for browser
    print("Waiting for browser connection...")
    time.sleep(2)

    # Create 100 cubes in a grid
    count = 100
    print(f"Creating InstancedMesh with {count} instances...")

    geometry = g.Box([0.08, 0.08, 0.08])
    material = g.MeshPhongMaterial(color=0x22aa44)
    instanced = g.InstancedMesh(geometry, material, count=count)

    # Set positions in a 10x10 grid
    for i in range(count):
        row = i // 10
        col = i % 10
        matrix = np.eye(4, dtype=np.float32)
        matrix[0, 3] = (col - 5) * 0.15  # x
        matrix[1, 3] = (row - 5) * 0.15  # y
        matrix[2, 3] = 0                  # z
        instanced.set_matrix_at(i, matrix)

    vis["test_instances"].set_object(instanced)
    print("InstancedMesh created!")

    # Animate
    print("Animating... Press Ctrl+C to stop.")
    frame = 0
    matrices = np.zeros((count, 4, 4), dtype=np.float32)

    try:
        while True:
            t = frame * 0.05

            for i in range(count):
                row = i // 10
                col = i % 10
                matrices[i] = np.eye(4, dtype=np.float32)
                matrices[i][0, 3] = (col - 5) * 0.15
                matrices[i][1, 3] = (row - 5) * 0.15
                matrices[i][2, 3] = 0.1 * np.sin(t + row * 0.5 + col * 0.3)

            vis["test_instances"].set_instance_matrices(matrices)
            frame += 1
            time.sleep(0.016)

    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
