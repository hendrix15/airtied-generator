import json

import yaml

from search.models import Node, Vector3


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
        for id, force in data["forces"].items():
            for node_id in force["nodes"]:
                node = next(node for node in nodes if node.id == node_id)
                node.load = Vector3(x=force["x"], y=force["y"], z=force["z"])
    return nodes


def load_config(filename: str) -> dict:
    with open(filename) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config
