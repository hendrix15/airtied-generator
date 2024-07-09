import json
import os
import uuid

from search.models import Bool3, Edge, Node, Vector3


def read_json(filename: str) -> tuple[list[Node], list[Edge]]:
    nodes = []
    edges = []
    with open(filename) as f:
        data = json.load(f)
        for id, coordinates in data["nodes"].items():
            if id in data["anchors"]:
                anchor = data["anchors"][id]
                nodes.append(
                    Node(
                        id=id,
                        vec=Vector3(
                            x=coordinates["x"], y=coordinates["y"], z=coordinates["z"]
                        ),
                        r_support=Bool3(x=anchor["rx"], y=anchor["ry"], z=anchor["rz"]),
                        t_support=Bool3(x=anchor["tx"], y=anchor["ty"], z=anchor["tz"]),
                        fixed=True,
                    )
                )
            else:
                nodes.append(
                    Node(
                        id=id,
                        vec=Vector3(
                            x=coordinates["x"], y=coordinates["y"], z=coordinates["z"]
                        ),
                        fixed=True,
                    )
                )
        if "forces" in data:
            for id, force in data["forces"].items():
                for node_id in force["nodes"]:
                    node = next(node for node in nodes if node.id == node_id)
                    node.load = Vector3(x=force["x"], y=force["y"], z=force["z"])
        if "edges" in data:
            for id, values in data["edges"].items():
                u = next(node for node in nodes if node.id == values["start"])
                v = next(node for node in nodes if node.id == values["end"])
                edges.append(Edge(id, u, v))
    return nodes, edges


def write_json(
    nodes: list[Node], edges: list[Edge], dirname: str, filename: str
) -> None:
    os.makedirs(dirname, exist_ok=True)
    result = {"nodes": {}, "edges": {}, "anchors": {}, "forces": {}}
    for node in nodes:
        result["nodes"][node.id] = {
            "x": float(node.vec.x),
            "y": float(node.vec.y),
            "z": float(node.vec.z),
        }
        if node.r_support and node.t_support:
            result["anchors"][node.id] = {
                "rx": node.r_support.x,
                "ry": node.r_support.y,
                "rz": node.r_support.z,
                "tx": node.t_support.x,
                "ty": node.t_support.y,
                "tz": node.t_support.z,
            }
        if node.load:
            try:
                force_id = next(
                    force_id
                    for force_id in result["forces"]
                    if result["forces"][force_id]["x"] == node.load.x
                    and result["forces"][force_id]["y"] == node.load.y
                    and result["forces"][force_id]["z"] == node.load.z
                )
                result["forces"][force_id]["nodes"].append(node.id)
            except StopIteration:
                force_id = str(uuid.uuid4())
                result["forces"][force_id] = {
                    "nodes": [node.id],
                    "x": node.load.x,
                    "y": node.load.y,
                    "z": node.load.z,
                }

    for edge in edges:
        result["edges"][edge.id] = {"start": edge.u.id, "end": edge.v.id}
    with open(f"{dirname}{filename}", "w") as f:
        json.dump(result, f)


def convert_obj_to_json(input_file: str, output_file: str) -> None:
    vertices = []
    edges = []
    with open(input_file) as f:
        for line in f:
            if line.startswith("v "):
                vertices.append(list(map(float, line.strip().split()[1:])))
            if line.startswith("l "):
                edges.append(list(map(int, line.strip().split()[1:])))
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
    with open(output_file, "w") as f:
        json.dump(result, f)


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
