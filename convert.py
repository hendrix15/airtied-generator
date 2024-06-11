import json
import uuid
from argparse import ArgumentParser

import matplotlib.pyplot as plt

from search.models import Edge, Node
from search.utils import read_json


def vertices_and_edges_from_obj(filename: str) -> tuple[list, list]:
    vertices = []
    edges = []
    with open(filename) as f:
        for line in f:
            if line.startswith("v "):
                vertices.append(list(map(float, line.strip().split()[1:])))
            if line.startswith("l "):
                edges.append(list(map(int, line.strip().split()[1:])))
    return vertices, edges


def nodes_and_edges_to_obj(filename: str, nodes: list[Node], edges: list[Edge]) -> None:
    with open(filename, "w") as obj_file:
        mapping = {node.id: i for i, node in enumerate(nodes, start=1)}
        vertices_output = [
            f"v {node.vec.x} {node.vec.y} {node.vec.z}\n" for node in nodes
        ]
        edges_output = [
            f"l {mapping[edge.u.id]} {mapping[edge.v.id]}\n" for edge in edges
        ]
        print(
            f"Writing {len(vertices_output)} vertices and {len(edges_output)} edges to file"
        )
        obj_file.writelines(vertices_output)
        obj_file.write("\n")
        obj_file.writelines(edges_output)
        obj_file.write("\n")


def vertices_and_edges_to_json(filename: str, vertices: list, edges: list) -> None:
    result = {"nodes": {}, "edges": {}, "anchors": {}, "forces": {}}
    mapping = {}
    for i, vertex in enumerate(vertices, start=1):
        node_id = str(uuid.uuid4())
        x = vertex[0]
        y = vertex[1]
        z = vertex[2]
        result["nodes"][node_id] = {"x": x, "y": y, "z": z}
        mapping[i] = node_id
    for edge in edges:
        edge_id = str(uuid.uuid4())
        u = mapping[edge[0]]
        v = mapping[edge[1]]
        result["edges"][edge_id] = {"start": u, "end": v}
    with open(f"{filename}", "w") as f:
        json.dump(result, f)


def visualize(nodes: list[Node], edges: list[Edge]) -> None:
    lines = [
        [
            (edge.u.vec.x, edge.u.vec.y, edge.u.vec.z),
            (edge.v.vec.x, edge.v.vec.y, edge.v.vec.z),
        ]
        for edge in edges
    ]

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    xs = [node.vec.x for node in nodes]
    ys = [node.vec.y for node in nodes]
    zs = [node.vec.z for node in nodes]

    ax.scatter(xs, zs, ys, marker="o")

    for line in lines:
        plt.plot(
            [line[0][0], line[1][0]],
            [line[0][2], line[1][2]],
            [line[0][1], line[1][1]],
            color="black",
        )

    ax.set_xlim(-5, 5)
    ax.set_ylim(5, 15)
    ax.set_zlim(0, 10)

    plt.show()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="dino.obj")
    parser.add_argument("--output", type=str, default="dino.json")
    args = parser.parse_args()

    vertices, edges = vertices_and_edges_from_obj(args.input)
    vertices_and_edges_to_json(args.output, vertices, edges)

    nodes, edges = read_json(args.output)
    visualize(nodes, edges)

    # Convert back to obj for verification
    # nodes_and_edges_to_obj("dino_test.obj", nodes, edges)


if __name__ == "__main__":
    main()
