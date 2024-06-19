import os

import matplotlib.pyplot as plt

from search.models import Edge, Node


def visualize(
    nodes: list[Node],
    edges: list[Edge],
    compression_edges: list[str] = [],
    tension_edges: list[str] = [],
    dirname: str | None = None,
    filename: str | None = None,
) -> None:
    normal_lines = [
        [
            (edge.u.vec.x, edge.u.vec.y, edge.u.vec.z),
            (edge.v.vec.x, edge.v.vec.y, edge.v.vec.z),
        ]
        for edge in edges
        if edge.id not in compression_edges and edge.id not in tension_edges
    ]
    compression_lines = [
        [
            (edge.u.vec.x, edge.u.vec.y, edge.u.vec.z),
            (edge.v.vec.x, edge.v.vec.y, edge.v.vec.z),
        ]
        for edge in edges
        if edge.id in compression_edges
    ]
    tension_lines = [
        [
            (edge.u.vec.x, edge.u.vec.y, edge.u.vec.z),
            (edge.v.vec.x, edge.v.vec.y, edge.v.vec.z),
        ]
        for edge in edges
        if edge.id in tension_edges
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
    for line in compression_lines:
        plt.plot(
            [line[0][0], line[1][0]],
            [line[0][2], line[1][2]],
            [line[0][1], line[1][1]],
            color="red",
        )
    for line in tension_lines:
        plt.plot(
            [line[0][0], line[1][0]],
            [line[0][2], line[1][2]],
            [line[0][1], line[1][1]],
            color="blue",
        )

    min_x = min(xs)
    max_x = max(xs)
    min_y = min(ys)
    max_y = max(ys)
    min_z = min(zs)
    max_z = max(zs)
    max_abs = max([abs(max_x - min_x), abs(max_y - min_y), abs(max_z - min_z)])

    ax.set_xlim(min_x, min_x + max_abs)
    ax.set_ylim(min_z, min_z + max_abs)
    ax.set_zlim(min_y, min_y + max_abs)

    if dirname and filename:
        os.makedirs(dirname, exist_ok=True)
        plt.savefig(f"{dirname}{filename}")
    else:
        plt.show()
