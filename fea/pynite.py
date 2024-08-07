import numpy as np
from PyNite import FEModel3D

from utils.models import Edge, Node


def fea_pynite(nodes: list[Node], edges: list[Edge]) -> dict:
    truss = FEModel3D()
    truss.add_material("Custom", 1, 1, 1, 1)

    for node in nodes:
        truss.add_node(node.id, node.vec.x, node.vec.y, node.vec.z)
        if node.r_support and node.t_support:
            truss.def_support(
                node.id,
                node.t_support.x,
                node.t_support.y,
                node.t_support.z,
                node.r_support.x,
                node.r_support.y,
                node.r_support.z,
            )
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
            "Custom",
            1,
            1,
            1,
            1,
        )
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

    # Add self weight of the beams
    # truss.add_member_self_weight("FY", -1)

    truss.analyze(check_statics=True, sparse=False)
    max_forces = {member.name: member.max_axial() for member in truss.Members.values()}
    if any(np.isnan(max_force) for max_force in max_forces.values()):
        raise Exception("At least one of the axial forces is nan")
    return max_forces
