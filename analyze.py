from argparse import ArgumentParser

import matplotlib.pyplot as plt

from search.models import Edge, Node
from search.utils import generate_FEA_truss, get_euler_load, read_json


def visualize(
    nodes: list[Node], edges: list[Edge], highlighted_edge_ids: list[str]
) -> None:
    normal_lines = [
        [
            (edge.u.vec.x, edge.u.vec.y, edge.u.vec.z),
            (edge.v.vec.x, edge.v.vec.y, edge.v.vec.z),
        ]
        for edge in edges
        if edge.id not in highlighted_edge_ids
    ]
    highlighted_lines = [
        [
            (edge.u.vec.x, edge.u.vec.y, edge.u.vec.z),
            (edge.v.vec.x, edge.v.vec.y, edge.v.vec.z),
        ]
        for edge in edges
        if edge.id in highlighted_edge_ids
    ]

    fig = plt.figure()
    ax = fig.add_subplot(projection="3d")

    xs = [node.vec.x for node in nodes]
    ys = [node.vec.y for node in nodes]
    zs = [node.vec.z for node in nodes]

    ax.scatter(xs, zs, ys, marker="o")

    for line in normal_lines:
        plt.plot(
            [line[0][0], line[1][0]],
            [line[0][2], line[1][2]],
            [line[0][1], line[1][1]],
            color="black",
        )

    for line in highlighted_lines:
        plt.plot(
            [line[0][0], line[1][0]],
            [line[0][2], line[1][2]],
            [line[0][1], line[1][1]],
            color="red",
        )

    ax.set_xlim(-5, 5)
    ax.set_ylim(5, 15)
    ax.set_zlim(0, 10)

    plt.show()


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="dino.json")
    args = parser.parse_args()

    nodes, edges = read_json(args.input)
    truss = generate_FEA_truss(nodes, edges)
    truss.analyze(check_statics=True)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}

    exceeded_edges = []
    for edge in edges:
        max_force = max_forces[edge.id]
        euler_load = get_euler_load(edge.length())
        if max_force > euler_load:
            exceeded_edges.append(edge.id)
            print(
                f"Member {edge.id}: Max force of {max_force} exceeds the euler load of {euler_load}"
            )

    print(
        f"The euler load is exceeded for {len(exceeded_edges)} of {len(edges)} members"
    )

    visualize(nodes, edges, exceeded_edges)


if __name__ == "__main__":
    main()
