from scipy.spatial import Delaunay
from random import randint
from pathlib import Path
from PyNite import FEModel3D
from PyNite import Visualization
from ..pipeline_draft.config import Material, MaxDim, SectionProperties
from argparse import ArgumentParser


# Units for this model are meters and kilonewtons

def test_mesh(mesh: Delaunay):
    model = FEModel3D()
    model.add_material(Material.name, Material.e, Material.g, Material.nu, Material.rho)
    for i, (x, y, z) in enumerate(mesh.points):
        model.add_node(f"N{i}", x, y, z)

    # let the ground nodes be support by the ground
    # TODO: I think we should only support DZ, as they can still move sideways?
    model.def_support(
        "N0",
        support_DX=True,
        support_DY=True,
        support_DZ=True,
        support_RX=True,
        support_RY=True,
        support_RZ=True,
    )
    model.def_support(
        "N1",
        support_DX=True,
        support_DY=True,
        support_DZ=True,
        support_RX=True,
        support_RY=True,
        support_RZ=True,
    )
    model.def_support(
        "N2",
        support_DX=True,
        support_DY=True,
        support_DZ=True,
        support_RX=True,
        support_RY=True,
        support_RZ=True,
    )

    seen = set()

    def add_truss_member(u, v):
        if (u, v) in seen:
            return
        model.add_member(
            f"M{u}-{v}",
            f"N{u}",
            f"N{v}",
            Material.name,
            SectionProperties.iy,
            SectionProperties.iz,
            SectionProperties.j,
            SectionProperties.a,
        )
        # TODO: not sure if every member should be released, in the example, there is one unreleased member
        model.def_releases(f"M{u}-{v}", False, False, False, False, True, True, \
                           False, False, False, False, True, True)
        seen.add((u, v))
        seen.add((v, u))

    for i, (t, u, v, w) in enumerate(mesh.simplices):
        add_truss_member(t, u)
        add_truss_member(t, v)
        add_truss_member(t, w)
        add_truss_member(u, v)
        add_truss_member(u, w)
        add_truss_member(v, w)

    

    num_nodes = len(mesh.points)
    model.add_node_load(f"N{num_nodes-3}", "FZ", -50)
    model.add_node_load(f"N{num_nodes-2}", "FZ", -50)
    model.add_node_load(f"N{num_nodes-1}", "FZ", -50)

    model.analyze(check_statics=True)
    
    for model_member in model.Members.values():
        print(f"Member {model_member.name} calculated axial force: {model_member.max_axial()}")
    # TODO: assert that deformation is below threshold

    # Visualization.render_model(model, render_loads=True, deformed_shape=True)


def write_tetra_mesh(filename: str, mesh: Delaunay):
    with open(filename, "w") as obj_file:
        vertices = [f"v {x} {y} {z}\n" for (x, y, z) in mesh.points]
        edges = set()
        for nodes in mesh.simplices:
            t, u, v, w = sorted(nodes)
            edges.add(f"l {t+1} {u+1}\n")
            edges.add(f"l {t+1} {v+1}\n")
            edges.add(f"l {t+1} {w+1}\n")
            edges.add(f"l {u+1} {v+1}\n")
            edges.add(f"l {u+1} {w+1}\n")
            edges.add(f"l {v+1} {w+1}\n")

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


def generate(
    num_objects: int,
    max_random_points: int,
    max_x: int,
    max_y: int,
    max_z: int,
    target_dir: Path,
):
    if target_dir.exists():
        if (
            input(
                f"'{target_dir}' already exists. All of its contents will be overwritten. Continue? (y/N) "
            )
            .lower()
            .strip()
            == "y"
        ):
            if target_dir.is_dir():
                for f in target_dir.iterdir():
                    f.unlink()
            else:
                target_dir.unlink()
    target_dir.mkdir(exist_ok=True)
    force_plane = [(20, 20, max_z), (30, 30, max_z), (20, 40, max_z)]

    for i in range(num_objects):
        n = randint(0, max_random_points)
        points = get_random_points_below_layer(*force_plane, n)
        tri = Delaunay(points)
        test_mesh(tri)
        write_tetra_mesh(target_dir / f"{i+1}.obj", tri)


def run():
    parser = ArgumentParser()
    parser.add_argument("num_objects", type=int)
    parser.add_argument("--max-random-points", type=int, default=20)
    parser.add_argument("--max-x", type=int, default=MaxDim.x)
    parser.add_argument("--max-y", type=int, default=MaxDim.y)
    parser.add_argument("--max-z", type=int, default=MaxDim.z)
    parser.add_argument(
        "--target-dir", type=Path, default=(Path(__file__).parent / "out")
    )
    args = parser.parse_args()
    generate(**dict(args._get_kwargs()))


if __name__ == "__main__":
    run()
