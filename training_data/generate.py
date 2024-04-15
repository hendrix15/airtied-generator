from scipy.spatial import Delaunay
from random import randint
from enum import IntEnum
from pathlib import Path


class MaxDim(IntEnum):
    x = 100
    y = 100
    z = 200


def test_mesh():
    pass


def write_tetra_mesh(filename: str, mesh: Delaunay):
    with open(filename, "w") as obj_file:
        vertices = [f"v {x} {y} {z}\n" for (x, y, z) in mesh.points]
        edges = []
        for t, u, v, w in mesh.simplices:
            edges.append(f"l {t+1} {u+1}\n")
            edges.append(f"l {t+1} {v+1}\n")
            edges.append(f"l {t+1} {w+1}\n")
            edges.append(f"l {u+1} {v+1}\n")
            edges.append(f"l {u+1} {w+1}\n")
            edges.append(f"l {v+1} {w+1}\n")

        v = len(vertices)
        faces = ["f 1 2 3\n", f"f {v-2} {v-1} {v}"]

        obj_file.writelines(vertices)
        obj_file.write("\n")
        obj_file.writelines(edges)
        obj_file.write("\n")
        obj_file.writelines(faces)


def get_random_point(
    min_x=0, min_y=0, min_z=0, max_x=MaxDim.x, max_y=MaxDim.y, max_z=MaxDim.z
):
    return randint(min_x, max_x), randint(min_y, max_y), randint(min_z, max_z)


def get_random_points_below_layer(p1, p2, p3, n):
    min_z = min(p1[2], p2[2], p3[2])
    points = [
        get_random_point(max_z=0),
        get_random_point(max_z=0),
        get_random_point(max_z=0),
    ]
    for _ in range(n):
        points.append(get_random_point(max_z=min_z))
    points.extend([p1, p2, p3])

    return points


def generate():
    out_path = Path(__file__).parent / "out"
    out_path.mkdir(exist_ok=True)
    force_plane = [(20, 20, MaxDim.z), (30, 30, MaxDim.z), (20, 40, MaxDim.z)]

    for i in range(1, 21):
        n = randint(0, 20)
        points = get_random_points_below_layer(*force_plane, n)
        tri = Delaunay(points)
        write_tetra_mesh(out_path / f"{i}.obj", tri)


if __name__ == "__main__":
    generate()
