import json

import yaml
from PyNite import FEModel3D

from search.config import Material, SectionProperties
from search.models import Edge, Node, Vector3


def read_json(filename: str) -> list[Node]:
    nodes = []
    with open(filename) as f:
        data = json.load(f)
        for id, coordinates in data["anchors"].items():
            nodes.append(
                Node(
                    id=id,
                    vec=Vector3(
                        x=coordinates["x"], y=coordinates["y"], z=coordinates["z"]
                    ),
                    support=True,
                )
            )
        for id, coordinates in data["nodes"].items():
            nodes.append(
                Node(
                    id=id,
                    vec=Vector3(
                        x=coordinates["x"], y=coordinates["y"], z=coordinates["z"]
                    ),
                    support=False,
                )
            )
        for id, force in data["forces"].items():
            for node_id in force["nodes"]:
                node = next(node for node in nodes if node.id == node_id)
                node.load = Vector3(x=force["x"], y=force["y"], z=force["z"])
    return nodes


def load_config(filename: str) -> dict:
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def generate_FEA_truss(nodes: list[Node], edges: list[Edge]) -> FEModel3D:
    truss = FEModel3D()
    truss.add_material(Material.name, Material.e, Material.g, Material.nu, Material.rho)

    for node in nodes:
        truss.add_node(node.id, node.vec.x, node.vec.y, node.vec.z)
        if node.support:
            truss.def_support(node.id, True, True, True, True, True, True)
        if node.load:
            if node.load.x != 0:
                truss.add_node_load(node.id, "FX", node.load.x)
            if node.load.y != 0:
                truss.add_node_load(node.id, "FY", node.load.y)
            if node.load.z != 0:
                truss.add_node_load(node.id, "FZ", node.load.z)

    for edge in edges:
        truss.add_member(
            edge.id,
            edge.u.id,
            edge.v.id,
            Material.name,
            SectionProperties.iy,
            SectionProperties.iz,
            SectionProperties.j,
            SectionProperties.a,
        )
        # do we have to release all edges??
        truss.def_releases(
            edge.id,
            False,
            False,
            False,
            False,
            True,
            True,
            False,
            False,
            False,
            False,
            True,
            True,
        )

    return truss
