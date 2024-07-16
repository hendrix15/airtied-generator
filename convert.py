import os
import uuid
from argparse import ArgumentParser

from utils.models import Bool3, Edge, Node, Vector3
from utils.parser import write_json


def read_obj(input_file: str) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    with open(input_file) as f:
        counter = 1
        mapping = {}
        for line in f:
            if line.startswith("v "):
                node_id = str(uuid.uuid4())
                coordinates = list(map(float, line.strip().split()[1:]))
                if coordinates[1] < 0.2:
                    node = Node(
                        id=node_id,
                        vec=Vector3(
                            x=coordinates[0], y=coordinates[1], z=coordinates[2]
                        ),
                        r_support=Bool3(x=False, y=False, z=False),
                        t_support=Bool3(x=True, y=True, z=True),
                        fixed=True,
                    )
                else:
                    node = Node(
                        id=node_id,
                        vec=Vector3(
                            x=coordinates[0], y=coordinates[1], z=coordinates[2]
                        ),
                        fixed=True,
                    )
                nodes.append(node)
                mapping[counter] = node
                counter += 1
            if line.startswith("l "):
                edge_id = str(uuid.uuid4())
                node_ids = list(map(int, line.strip().split()[1:]))
                edge = Edge(id=edge_id, u=mapping[node_ids[0]], v=mapping[node_ids[1]])
                edges.append(edge)
    return nodes, edges


def write_obj(filename: str, nodes: list[Node], edges: list[Edge]) -> None:
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


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="dino.obj")
    parser.add_argument("--output", type=str, default="dino.json")
    args = parser.parse_args()

    nodes, edges = read_obj(args.input)
    dirname, filename = os.path.split(args.output)
    write_json(nodes=nodes, edges=edges, dirname=f"{dirname}/", filename=filename)

    # Convert back to obj for verification
    # write_obj("test.obj", nodes, edges)


if __name__ == "__main__":
    main()
